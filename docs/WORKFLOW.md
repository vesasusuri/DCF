# Development Workflow

Branching strategy, PR process, CI/CD pipeline, and team conventions.

---

## Branching Strategy

```
main                    Production-ready code, protected branch
  └── develop           Integration branch, deployed to staging
       ├── feature/*    New features (feature/P1-04-excel-mapping)
       ├── fix/*        Bug fixes (fix/lease-date-parsing)
       └── chore/*      Infra, docs, tooling (chore/update-alembic)
```

### Rules

- **`main`** — Protected. Merge only via PR from `develop`. Triggers production deploy.
- **`develop`** — Protected. Merge only via PR from feature branches. Triggers staging deploy.
- Feature branches follow the task naming convention: `feature/P1-04-excel-mapping`, `feature/P2-01-doc-classification`.
- Rebase onto `develop` before creating PR (clean linear history).
- Delete branches after merge.

---

## PR Process

### 1. Create Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/P1-04-excel-mapping
```

### 2. Develop

- Write code following [Onion Architecture](ONION_ARCHITECTURE.md) layer rules.
- Write tests alongside code (domain tests first, integration tests second).
- Run locally before pushing:

```bash
make lint     # ruff + mypy
make test     # pytest
```

### 3. Open PR

- Title: `[P1-04] Excel Parsing & Data Mapping Engine`
- Description: What changed, why, how to test, screenshots if UI.
- Link to the task in the playbook for context.
- Request review from at least 1 team member.

### 4. CI Checks (automated)

All checks must pass before merge:

```
┌─────────┐     ┌────────────┐     ┌─────────┐     ┌─────────┐
│  Lint   │ ──► │ Type Check │ ──► │  Test   │ ──► │  Build  │
│ ruff    │     │   mypy     │     │ pytest  │     │ docker  │
└─────────┘     └────────────┘     └─────────┘     └─────────┘
```

### 5. Code Review

- Reviewer checks: correctness, architecture compliance, test coverage, domain accuracy.
- For calculation changes: verify against Excel ground truth test cases.
- For AI extraction changes: check evaluation metrics haven't regressed.

### 6. Merge

- Squash merge into `develop`.
- CI auto-deploys to staging.
- After validation on staging, PR from `develop` → `main` for production.

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### `ci.yml` — Runs on every push and PR

```yaml
jobs:
  lint:
    - ruff check backend/
    - ruff format --check backend/
    - mypy backend/app/

  test-backend:
    services:
      postgres: postgres:16
      redis: redis:7
    steps:
      - pytest backend/tests/ --cov --cov-report=xml
      - Upload coverage report

  test-frontend:
    steps:
      - cd frontend && npm ci
      - npm run type-check
      - npm run test
      - npm run build  # Verify production build succeeds

  build:
    needs: [lint, test-backend, test-frontend]
    steps:
      - docker build -t dcf-api backend/
      - docker build -t dcf-frontend frontend/
```

#### `deploy-staging.yml` — Runs on merge to `develop`

```yaml
jobs:
  deploy:
    - Push Docker images to registry
    - Run Alembic migrations on staging DB
    - Deploy containers to staging environment
    - Run smoke tests
    - Notify team on Slack
```

#### `deploy-production.yml` — Runs on merge to `main`

```yaml
jobs:
  deploy:
    - Push Docker images with release tag
    - Run Alembic migrations on production DB
    - Deploy with rolling update (zero downtime)
    - Run smoke tests
    - Notify team + create GitHub release
```

---

## Local Development

### First-Time Setup

```bash
git clone git@github.com:colliers-de/dcf-platform.git
cd dcf-platform
cp .env.example .env               # Set local environment variables
docker-compose up -d                # Start all services
make migrate                        # Run database migrations
make seed                           # Load sample pilot data
```

### Daily Workflow

```bash
docker-compose up -d                # Start services (if stopped)
cd backend && uv run uvicorn app.main:app --reload   # API with hot-reload
cd frontend && npm run dev          # Vite dev server with HMR
```

### Makefile Shortcuts

| Command | Action |
|---------|--------|
| `make up` | `docker-compose up -d` |
| `make down` | `docker-compose down` |
| `make test` | Run all pytest tests |
| `make lint` | Run ruff + mypy |
| `make migrate` | Run Alembic migrations |
| `make seed` | Load pilot data |
| `make reset-db` | Drop and recreate database |

---

## Code Conventions

### Python (Backend)

- **Formatter**: ruff format (black-compatible)
- **Linter**: ruff (replaces flake8, isort, pylint)
- **Type checker**: mypy (strict mode)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Google-style for public functions

### TypeScript (Frontend)

- **Formatter**: Prettier
- **Linter**: ESLint with TypeScript rules
- **Naming**: camelCase for functions/variables, PascalCase for components/types
- **Components**: Functional components with hooks (no class components)

### Commits

Follow Conventional Commits:

```
feat(P1-04): add Excel column mapping engine
fix(P1-06): correct indexation compounding for CPI leases
test(P1-22): add reconciliation tests for sample portfolio
docs: update API design with new assumption endpoints
chore: upgrade SQLAlchemy to 2.0.30
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://dcf:dcf@localhost:5432/dcf_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# File Storage
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=dcf-files
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# AI / LLM
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_KEY=xxx
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Auth
JWT_SECRET=dev-secret-change-in-production
JWT_EXPIRY_MINUTES=30
JWT_REFRESH_EXPIRY_DAYS=7

# App
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:5173
```
