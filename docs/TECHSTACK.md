# Tech Stack

Every technology in the stack is chosen for a specific project requirement — institutional audit, DCF calculation precision, German lease PDF extraction, or developer velocity.

---

## Overview

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend API | Python + FastAPI | 3.12 / 0.110+ |
| ORM | SQLAlchemy (async) + Alembic | 2.0 |
| Database | PostgreSQL | 16 |
| Cache / Queue Broker | Redis | 7 |
| Task Queue | Celery or arq | — |
| File Storage | MinIO (dev) / S3 or Azure Blob (prod) | — |
| Frontend | React + Vite | 18 / 5+ |
| Language | TypeScript | 5.4+ |
| Styling | Tailwind CSS | 3.4+ |
| Routing | React Router | 6+ |
| Components | shadcn/ui | latest |
| Charts | Recharts or Tremor | — |
| AI / LLM | Azure OpenAI GPT-4o or Anthropic Claude | — |
| Containerization | Docker + docker-compose | 24+ / 2.20+ |
| CI/CD | GitHub Actions | — |
| Auth | JWT (SSO/OIDC-ready for Phase 3) | — |

---

## Detailed Rationale

### Backend: Python 3.12 + FastAPI

**Why Python?** The platform's core is a DCF calculation engine. Python is the dominant language for financial modelling with mature libraries (`numpy`, `pandas`, `decimal`). It's also the primary language for every major AI/ML library the extraction pipeline needs.

**Why FastAPI?** Automatic OpenAPI docs (critical for multi-team development), Pydantic validation (catches bad data before it hits the engine), and native async support for handling concurrent valuation runs.

**Why not Django?** Django ORM would force the entire Django framework — overkill since FastAPI already covers routing and validation. We need fine-grained query control for complex portfolio aggregations.

**Why not Node.js / Go / Java?** None have Python's financial modelling and AI/ML ecosystem depth. Go and Java would require separate services for the calculation engine and extraction pipeline anyway.

### ORM: SQLAlchemy 2.0 (async) + Alembic

**Why SQLAlchemy?** The data model is complex — projects, assets, leases, assumptions, scenarios, run results — with deep relational joins. SQLAlchemy gives full control over query optimization while keeping code readable.

**Why Alembic?** Versioned, auditable schema migrations — a must for institutional clients who need to trace every database change. Each migration is a numbered, reviewable file in version control.

### Database: PostgreSQL 16

**Why PostgreSQL?** The concept doc requires an immutable audit trail with Run-ID principle and full traceability. PostgreSQL offers:
- **JSONB columns** — Flexible assumption schemas (different asset types have different fields) alongside strict relational integrity.
- **Row-level security** — Multi-tenant access control at the database level.
- **Range types** — Native support for lease date ranges.
- **CTEs and window functions** — Complex DCF aggregation queries and time-series cash flow analysis.
- **`GENERATED ALWAYS AS IDENTITY`** — Tamper-resistant ID sequences.

**Why not MySQL?** Lacks JSONB, range types, and row-level security. PostgreSQL's query planner is significantly better for the analytical queries this platform requires.

**Why not MongoDB?** Cannot enforce the relational integrity this domain demands. Lease → tenant → property → portfolio relationships require foreign keys and join integrity.

### Cache / Queue Broker: Redis 7

Three roles:
1. **Task queue broker** for Celery/arq background jobs
2. **Caching** of computed DCF results so dashboards load instantly on repeat visits
3. **Session / rate-limit store** without hitting PostgreSQL

### Task Queue: Celery or arq

**Why async workers?** DCF runs for a 200-asset portfolio take 30–60 seconds. PDF extraction via LLM takes 10–30s per document. These cannot block the API. A task queue lets the backend return immediately while workers process in the background, with status updates via polling or WebSocket.

**Celery** is the mature choice with broad monitoring (Flower). **arq** is a lighter async-native alternative if the team prefers simplicity.

### File Storage: MinIO (dev) / S3 or Azure Blob (prod)

**Why not store files in the database?** Users upload rent rolls (Excel), lease PDFs, and the system generates export PDFs and Excel workbooks. Binary files in PostgreSQL kill backup performance and bloat WAL logs.

S3-compatible storage gives:
- Cheap, scalable storage
- Presigned URLs for secure direct downloads
- Lifecycle policies to auto-archive old uploads
- MinIO provides an identical local dev experience without cloud costs

### Frontend: React 18 + Vite

**Why React?** The wireframe doc defines 16+ screens with heavy interactivity — drag-and-drop mapping, real-time scenario comparison, drill-down cash flow tables, interactive charts. React has the largest ecosystem for complex UI patterns and the deepest hiring pool.

**Why Vite over Next.js?** The app is an internal SPA — no SEO needed, no public pages. Vite gives faster HMR, simpler config, and no server-side rendering complexity.

### Language: TypeScript

**Why not plain JavaScript?** The DCF domain has dozens of entity types (Project, Asset, Lease, Assumption, Scenario, RunResult, CashFlowRow…) with strict numeric precision requirements. TypeScript catches type mismatches at build time. When backend Pydantic schemas change, frontend types break immediately — invaluable for a calculation platform.

### Styling: Tailwind CSS

**Why not CSS Modules / styled-components?** The wireframes show a clean, data-dense UI with consistent spacing and typography. Tailwind's utility classes match this perfectly — no context-switching to separate CSS files. Tree-shaking produces smaller bundles.

### Routing: React Router

The wireframe workflow is sequential (S01→S10) but users also need deep-linking to specific assets, scenarios, and results. React Router handles protected routes (auth guard), nested layouts (sidebar + top bar), and URL-based state (e.g., `/projects/123/runs/456/results`).

### Components: shadcn/ui

**Why not Material UI / Ant Design / Chakra?** The wireframes show a minimal, professional design — not a consumer app. shadcn/ui gives unstyled, accessible base components that are **copied into the codebase** (not a dependency):
- Full control over styling to match the wireframe aesthetic
- No version-lock to a component library
- Tailwind-native integration

### Charts: Recharts or Tremor

The wireframes (S07, S08, K1–K3) show cash flow waterfall charts, portfolio KPI dashboards, and sensitivity analysis graphs. **Recharts** is built on React + D3 with declarative composable components. **Tremor** is built specifically for dashboard UIs on top of Tailwind + Recharts — pre-built KPI cards, area/bar charts, and tables that match the wireframe patterns.

### AI / LLM: Azure OpenAI GPT-4o or Anthropic Claude

The platform extracts structured data from German-language lease PDFs with legal precision. GPT-4o and Claude are the only models with:
1. Strong German-language comprehension
2. Long context windows (128K+) for multi-page lease documents
3. Reliable structured JSON output for schema-driven extraction

**Azure OpenAI** satisfies the data residency requirement (EU hosting) for Colliers' institutional compliance. Open-source models (LLaMA, Mistral) don't yet match extraction accuracy on German legal/commercial text.

### Containerization: Docker + docker-compose

The stack has 5+ services (API, frontend, DB, Redis, MinIO, worker). Docker Compose lets any developer run the entire platform with one command. The same images deploy to production with zero config drift.

### CI/CD: GitHub Actions

Zero infrastructure to maintain (no Jenkins server), native Docker build/push, branch protection rules for the audit trail. Pipeline: `lint → type-check → test → build → deploy-staging`.

### Auth: JWT

The SPA architecture means frontend and backend are separate services. JWT provides stateless auth that works across services. Refresh tokens handle session extension. The concept doc mentions SSO/OIDC readiness for Phase 3 — JWT is the foundation that OIDC providers (Azure AD, Okta) issue natively.
