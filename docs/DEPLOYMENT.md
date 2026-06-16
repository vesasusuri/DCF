# Deployment & Infrastructure

Docker setup, environments, CI/CD pipeline, monitoring, and production operations.

---

## Environments

| Environment | Purpose | Deploy Trigger | URL |
|-------------|---------|---------------|-----|
| **Local** | Development | `docker-compose up` | `localhost:5173` (frontend), `localhost:8000` (API) |
| **Staging** | QA, UAT, demo | Merge to `develop` | `staging.dcf.colliers.de` |
| **Production** | Live | Merge to `main` | `dcf.colliers.de` |

---

## Docker Configuration

### docker-compose.yml (Local Development)

```yaml
version: "3.9"

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app          # Hot-reload
    environment:
      - DATABASE_URL=postgresql+asyncpg://dcf:dcf@db:5432/dcf_platform
      - REDIS_URL=redis://redis:6379/0
      - S3_ENDPOINT=http://minio:9000
      - S3_BUCKET=dcf-files
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin
      - ENVIRONMENT=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    command: ["celery", "-A", "app.worker", "worker", "--loglevel=info"]
    volumes:
      - ./backend:/app
    environment:
      # Same as api
    depends_on:
      - api

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src   # HMR
    environment:
      - VITE_API_URL=http://localhost:8000

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: dcf_platform
      POSTGRES_USER: dcf
      POSTGRES_PASSWORD: dcf
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dcf"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"     # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  miniodata:
```

### Backend Dockerfile (Multi-Stage)

```dockerfile
# Stage 1: Development (hot-reload)
FROM python:3.12-slim AS development
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install --system -e ".[dev]"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 2: Production
FROM python:3.12-slim AS production
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install --system .
COPY app/ app/
RUN adduser --disabled-password --no-create-home appuser
USER appuser
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Frontend Dockerfile

```dockerfile
# Development
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

---

## Production Architecture

```
                  Internet
                     │
              ┌──────┴──────┐
              │ Load Balancer│  (nginx / cloud ALB)
              │   TLS term.  │
              └──┬───────┬──┘
                 │       │
          ┌──────┴──┐ ┌──┴──────┐
          │ API #1  │ │ API #2  │   (FastAPI containers, auto-scale)
          └────┬────┘ └────┬────┘
               │           │
          ┌────┴───────────┴────┐
          │   Internal Network   │
          └─┬──────┬──────┬────┘
            │      │      │
      ┌─────┴─┐ ┌──┴───┐ ┌┴──────┐
      │  DB   │ │Redis │ │  S3   │   (Managed services)
      │(RDS)  │ │(Elast│ │(Blob) │
      └───────┘ │Cache)│ └───────┘
                └──────┘
            │
      ┌─────┴──────┐
      │ Worker #1  │   (Celery/arq, scale by queue depth)
      │ Worker #2  │
      └────────────┘
```

### Scaling Rules

| Service | Scaling | Trigger |
|---------|---------|---------|
| API | Horizontal (2–8 instances) | CPU > 70% or request latency > 500ms |
| Worker | Horizontal (2–6 instances) | Queue depth > 10 or job wait time > 30s |
| PostgreSQL | Vertical (resize) | CPU > 80% or connection count > 80% max |
| Redis | Vertical | Memory > 75% |
| S3 / Blob | N/A (managed, infinite) | — |

---

## CI/CD Pipeline

### GitHub Actions Workflow

```
Push to any branch:
  └── lint → type-check → test → build images

Merge to develop:
  └── all above + push images → deploy staging → smoke test → notify

Merge to main:
  └── all above + tag release → deploy production → smoke test → notify
```

### Deployment Steps (Staging / Production)

```bash
# 1. Build and push Docker images
docker build -t registry/dcf-api:$SHA backend/
docker build -t registry/dcf-frontend:$SHA frontend/
docker push registry/dcf-api:$SHA
docker push registry/dcf-frontend:$SHA

# 2. Run database migrations
kubectl exec deploy/dcf-api -- alembic upgrade head

# 3. Rolling update
kubectl set image deploy/dcf-api api=registry/dcf-api:$SHA
kubectl set image deploy/dcf-worker worker=registry/dcf-api:$SHA
kubectl set image deploy/dcf-frontend frontend=registry/dcf-frontend:$SHA

# 4. Smoke tests
curl -f https://staging.dcf.colliers.de/api/v1/health
```

---

## Monitoring & Observability

### Application Metrics

| Metric | Tool | Alert Threshold |
|--------|------|----------------|
| API response time (p95) | Application metrics | > 2s |
| API error rate (5xx) | Application metrics | > 1% |
| DCF calculation duration | Custom metric | > 120s for 100 assets |
| AI extraction duration | Custom metric | > 60s per document |
| Task queue depth | Celery/arq metrics | > 20 pending |
| Task failure rate | Celery/arq metrics | > 5% |

### Infrastructure Metrics

| Metric | Tool | Alert Threshold |
|--------|------|----------------|
| CPU utilisation | Cloud monitoring | > 80% sustained |
| Memory utilisation | Cloud monitoring | > 85% |
| Disk usage (DB) | Cloud monitoring | > 80% |
| DB connection pool | PostgreSQL stats | > 80% max connections |
| Redis memory | Redis INFO | > 75% maxmemory |

### Logging

```python
# Structured JSON logging
import structlog

logger = structlog.get_logger()

logger.info("valuation_run_started",
    run_id=run.id,
    project_id=run.project_id,
    total_assets=run.total_assets,
    model_version=run.model_version,
)
```

All logs shipped to centralised log aggregation (CloudWatch Logs / Azure Monitor / ELK).

### Health Check Endpoint

```
GET /api/v1/health
→ 200: {
    "status": "healthy",
    "version": "1.2.0",
    "database": "connected",
    "redis": "connected",
    "storage": "connected",
    "uptime_seconds": 86400
  }
```

---

## Backup & Disaster Recovery

| Component | Strategy | RPO | RTO |
|-----------|----------|-----|-----|
| PostgreSQL | Automated daily snapshots + continuous WAL archiving | < 1 hour | < 4 hours |
| S3 / Blob | Cross-region replication (if required) | 0 (synchronous) | < 1 hour |
| Redis | No backup needed (reconstructable from DB) | N/A | Minutes (restart) |
| Application | Container images in registry; infrastructure as code | 0 | < 30 min |

### Restore Procedure

Documented and tested quarterly:
1. Restore PostgreSQL from snapshot
2. Verify data integrity (run checksum queries)
3. Point application to restored DB
4. Verify S3 file access
5. Run smoke tests
6. Switch DNS (if full failover)
