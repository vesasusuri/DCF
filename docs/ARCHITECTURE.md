# System Architecture

High-level architecture of the AI-DCF Valuation Platform — service boundaries, data flows, and integration points.

---

## Design Principles

1. **Deterministic engine, AI-assisted ingestion** — The DCF calculation is pure math with no LLM involvement. AI only operates in the ingestion/extraction layer.
2. **Onion Architecture** — Domain logic has zero external dependencies. See [ONION_ARCHITECTURE.md](ONION_ARCHITECTURE.md) for the detailed layer breakdown.
3. **Single Run-ID principle** — Every output traces to one immutable `run_id` with locked model version and assumption snapshot.
4. **Stateless API, stateful workers** — API servers are horizontally scalable. Long-running jobs (DCF runs, PDF extraction) execute on dedicated workers.
5. **Event-driven audit** — Every mutation emits an audit event. The audit log is append-only and immutable.

---

## Reference Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  React SPA (Vite)  ·  Browser  ·  Future: Client Portal │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   API Gateway + Auth                     │
│              JWT validation · Rate limiting               │
│              CORS · Request logging                       │
└───┬──────────┬──────────────┬──────────────┬────────────┘
    │          │              │              │
    ▼          ▼              ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│Ingest- │ │   AI     │ │   DCF    │ │  Reporting   │
│  ion   │ │Extract-  │ │  Engine  │ │   Service    │
│Service │ │  ion     │ │          │ │              │
└───┬────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
    │           │             │              │
    ▼           ▼             ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│Object  │ │  LLM     │ │PostgreSQL│ │  PDF/XLSX    │
│Storage │ │Provider  │ │Valuation │ │   Output     │
│(S3)    │ │(Azure    │ │   DB     │ │  (S3)        │
│        │ │ OpenAI)  │ │          │ │              │
└────────┘ └──────────┘ └──────────┘ └──────────────┘
                  │
           ┌──────┴──────┐
           │   Redis     │
           │ Queue/Cache │
           └─────────────┘

        ┌─────────────────────────────────────┐
        │    Audit Log · Model Version ·      │
        │    Data Lineage (append-only)       │
        └─────────────────────────────────────┘
```

---

## Service Boundaries

### 1. Frontend (React SPA)

| Aspect | Detail |
|--------|--------|
| Runtime | Browser (no server-side rendering) |
| Build | Vite → static assets served by CDN or nginx |
| Auth | JWT stored in httpOnly cookie or secure localStorage |
| API | REST calls to backend via `fetchWithAuth()` wrapper |
| State | React Query for server state, React Context for app state |

### 2. Backend API (FastAPI)

| Aspect | Detail |
|--------|--------|
| Runtime | Python 3.12, uvicorn (async) |
| Responsibilities | Authentication, authorization, CRUD, orchestration, validation |
| Pattern | Onion Architecture — routes → services → domain → infrastructure |
| API format | RESTful JSON, OpenAPI auto-generated docs |
| Concurrency | Async endpoints for I/O, sync for CPU-bound calculation dispatch |

### 3. DCF Calculation Engine

| Aspect | Detail |
|--------|--------|
| Runtime | Python, invoked by backend workers (Celery/arq) |
| Pattern | Pure functions — no database access, no side effects |
| Input | Frozen assumption snapshot + lease data (passed as data objects) |
| Output | Cash flow arrays, valuation KPIs, sensitivity grids |
| Testability | 100% unit-testable against Excel ground truth |

### 4. AI Extraction Service

| Aspect | Detail |
|--------|--------|
| Runtime | Python, invoked by backend workers |
| LLM provider | Azure OpenAI GPT-4o or Anthropic Claude |
| Pipeline | Classify → Extract (schema-driven) → Validate → Score confidence |
| Output | Structured JSON with field-level confidence + source page citations |
| Human loop | Low-confidence fields flagged for review in S04 screen |

### 5. Reporting Service

| Aspect | Detail |
|--------|--------|
| Runtime | Python worker (async, triggered by API) |
| Excel | openpyxl — multi-sheet workbook with formulas and formatting |
| PDF | WeasyPrint or wkhtmltopdf — HTML template → styled PDF |
| Storage | Generated files uploaded to S3, permalink returned to frontend |

---

## Data Flow: End-to-End Valuation

```
User uploads files (Excel rent roll, lease PDFs)
        │
        ▼
[1] Ingestion Service
    ├── Classify document type
    ├── Store originals in S3
    └── Queue for processing
        │
        ▼
[2] Data Mapping (Excel) or AI Extraction (PDF)
    ├── Excel: Column mapping → canonical schema
    ├── PDF: LLM extraction → structured JSON
    ├── Deterministic validation (arithmetic, dates, plausibility)
    └── Confidence scoring
        │
        ▼
[3] Human Review (S03/S04 screens)
    ├── Accept / edit / reject extracted fields
    ├── Corrections logged to audit trail
    └── Approved data enters canonical DB
        │
        ▼
[4] Assumption Configuration (S05 screen)
    ├── Global defaults + asset-level overrides
    ├── Scenario creation (base, upside, downside)
    └── All changes attributed and timestamped
        │
        ▼
[5] DCF Calculation Run
    ├── Freeze assumptions + data snapshot (immutable)
    ├── Assign Run-ID and model version
    ├── Execute: lease → unit → asset → portfolio aggregation
    ├── Monthly cash flow waterfall
    └── Output: GAV, NPV, IRR, yields, sensitivity grids
        │
        ▼
[6] Results & Reporting (S07/S08/S10 screens)
    ├── Interactive dashboards with drill-down
    ├── Excel workbook export (10 sheets)
    ├── PDF report export (institutional format)
    └── All outputs linked to Run-ID
```

---

## Infrastructure Topology

### Local Development

```
docker-compose.yml
├── api         (Python FastAPI, hot-reload, volume mount)
├── worker      (Celery/arq, same codebase)
├── frontend    (Vite dev server, hot-reload)
├── db          (PostgreSQL 16, persistent volume)
├── redis       (Redis 7, caching + queue)
└── minio       (S3-compatible file storage)
```

### Production

```
Load Balancer (nginx / cloud ALB)
├── API instances (2+, horizontal scale)
├── Worker instances (2+, scale by queue depth)
├── Frontend (static assets on CDN)
├── PostgreSQL (managed: RDS / Azure Database)
├── Redis (managed: ElastiCache / Azure Cache)
├── S3 / Azure Blob (file storage)
└── Monitoring (application logs, calculation logs, extraction metrics)
```

---

## Cross-Cutting Concerns

| Concern | Approach |
|---------|----------|
| **Authentication** | JWT with refresh tokens; SSO/OIDC ready (Phase 3) |
| **Authorization** | RBAC with project-level permissions; row-level security in PostgreSQL |
| **Audit Trail** | Append-only audit_event table; every mutation logged with user, timestamp, old/new value, reason |
| **Model Versioning** | Calculation engine version stored per run; allows reproducibility |
| **Error Handling** | Structured error responses; retry logic on workers; dead-letter queue for failed jobs |
| **Observability** | Structured logging (JSON), request tracing, calculation latency metrics, extraction quality metrics |
