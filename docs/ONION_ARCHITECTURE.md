# Onion Architecture

The backend follows **Onion (Clean) Architecture** — domain logic sits at the centre with zero external dependencies. All infrastructure, frameworks, and I/O adapt to the domain through interfaces, never the other way around.

---

## Why Onion Architecture?

This platform has a complex, regulation-sensitive domain (institutional DCF valuation). The calculation engine, assumption rules, and audit logic must be:

1. **Testable without infrastructure** — Unit tests run without a database, Redis, or S3.
2. **Framework-independent** — Swapping FastAPI for another framework touches only the outer ring.
3. **LLM-independent** — The AI extraction layer is an infrastructure detail. The domain defines _what_ data it needs; infrastructure decides _how_ to get it.
4. **Auditable** — Business rules live in one place, not scattered across routes, ORM models, and utility functions.

---

## Layer Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     API / Presentation                        │
│         FastAPI routes, request/response schemas,             │
│         dependency injection, middleware                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  Application Services                   │  │
│  │        Use cases, orchestration, command handlers,      │  │
│  │        transaction boundaries                           │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │                   Domain Core                     │  │  │
│  │  │      Entities, value objects, domain services,    │  │  │
│  │  │      repository interfaces, domain events,        │  │  │
│  │  │      calculation engine                           │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    Infrastructure                       │  │
│  │     PostgreSQL repos, S3 storage, Redis cache,          │  │
│  │     LLM clients, email, PDF/Excel generation            │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**The dependency rule:** arrows point inward. Inner layers never import from outer layers.

---

## Layer Definitions

### Layer 1: Domain Core (`app/domain/`)

The innermost ring. Pure Python — no SQLAlchemy, no FastAPI, no Redis, no imports from any framework.

| Component | Purpose | Example |
|-----------|---------|---------|
| **Entities** | Core business objects with identity and lifecycle | `Project`, `Asset`, `Lease`, `ValuationRun` |
| **Value Objects** | Immutable data without identity | `Money`, `DateRange`, `GeoCoordinate`, `RunID` |
| **Domain Services** | Business logic spanning multiple entities | `CashFlowCalculator`, `AssumptionValidator` |
| **Repository Interfaces** | Abstract contracts for data access (no implementation) | `IProjectRepository`, `ILeaseRepository` |
| **Domain Events** | Facts about things that happened | `RunCompleted`, `AssumptionChanged`, `LeaseApproved` |
| **Exceptions** | Domain-specific error types | `InvalidAssumption`, `RunNotFound`, `AuditViolation` |
| **Calculation Engine** | Pure functions for DCF math | `calculate_cash_flow()`, `discount_to_pv()`, `compute_irr()` |

```python
# app/domain/entities/lease.py — No imports from SQLAlchemy, FastAPI, etc.

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from app.domain.value_objects import Money, DateRange

@dataclass
class Lease:
    id: str
    tenant_name: str
    unit_id: str
    term: DateRange
    passing_rent: Money
    indexation_type: str          # "CPI" | "fixed" | "capped"
    indexation_rate: Decimal | None
    break_option_date: date | None
    has_extension_option: bool

    def is_active(self, as_of: date) -> bool:
        return self.term.contains(as_of)

    def months_to_expiry(self, as_of: date) -> int:
        if not self.is_active(as_of):
            return 0
        return self.term.months_until_end(as_of)
```

```python
# app/domain/interfaces/repositories.py — Abstract base, no DB details

from abc import ABC, abstractmethod
from app.domain.entities.project import Project

class IProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Project | None: ...

    @abstractmethod
    async def save(self, project: Project) -> None: ...

    @abstractmethod
    async def list_by_organisation(self, org_id: str) -> list[Project]: ...
```

### Layer 2: Application Services (`app/services/`)

Orchestration layer. Coordinates domain objects, enforces transaction boundaries, and emits events. May import from `domain/` but never from `infrastructure/` or `api/`.

| Component | Purpose | Example |
|-----------|---------|---------|
| **Use-Case Services** | One class/function per business operation | `CreateProjectService`, `TriggerValuationRunService` |
| **Command/Query Objects** | Typed inputs for use cases | `CreateProjectCommand`, `RunValuationQuery` |
| **DTOs** | Data transfer objects between layers | `ProjectSummaryDTO`, `RunResultDTO` |

```python
# app/services/valuation_run_service.py

from app.domain.interfaces.repositories import IProjectRepository, IRunRepository
from app.domain.interfaces.file_storage import IFileStorage
from app.domain.services.cash_flow_calculator import CashFlowCalculator
from app.domain.entities.valuation_run import ValuationRun

class TriggerValuationRunService:
    def __init__(
        self,
        project_repo: IProjectRepository,
        run_repo: IRunRepository,
        calculator: CashFlowCalculator,
    ):
        self._project_repo = project_repo
        self._run_repo = run_repo
        self._calculator = calculator

    async def execute(self, project_id: str, scenario_id: str, user_id: str) -> str:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

        # Freeze assumptions into immutable snapshot
        run = ValuationRun.create(
            project=project,
            scenario_id=scenario_id,
            triggered_by=user_id,
        )
        await self._run_repo.save(run)

        # Dispatch to background worker (returns run_id immediately)
        return run.id
```

### Layer 3: API / Presentation (`app/api/`)

The outermost application layer. Translates HTTP into service calls and service results into HTTP responses. Handles dependency injection.

| Component | Purpose | Example |
|-----------|---------|---------|
| **Routes** | FastAPI endpoint definitions | `projects_router.py`, `runs_router.py` |
| **Schemas** | Pydantic request/response models | `CreateProjectRequest`, `RunResultResponse` |
| **Dependencies** | FastAPI `Depends()` for DI | `get_current_user()`, `get_project_service()` |
| **Middleware** | Request logging, CORS, error handling | `audit_middleware.py` |

```python
# app/api/routes/valuation_runs.py

from fastapi import APIRouter, Depends
from app.api.dependencies import get_run_service, get_current_user
from app.api.schemas.runs import TriggerRunRequest, TriggerRunResponse

router = APIRouter(prefix="/valuation-runs", tags=["Valuation Runs"])

@router.post("/", response_model=TriggerRunResponse)
async def trigger_run(
    req: TriggerRunRequest,
    service = Depends(get_run_service),
    user = Depends(get_current_user),
):
    run_id = await service.execute(req.project_id, req.scenario_id, user.id)
    return TriggerRunResponse(run_id=run_id, status="queued")
```

### Layer 4: Infrastructure (`app/infrastructure/`)

Implements the interfaces defined by the domain. This is where all external dependencies live — databases, file storage, LLM providers, email services.

| Component | Purpose | Example |
|-----------|---------|---------|
| **Repository Implementations** | SQLAlchemy-backed repos | `SqlProjectRepository`, `SqlLeaseRepository` |
| **ORM Models** | SQLAlchemy table definitions | `ProjectModel`, `LeaseModel` |
| **File Storage** | S3/MinIO adapter | `S3FileStorage` implements `IFileStorage` |
| **LLM Client** | Azure OpenAI / Claude adapter | `AzureOpenAIExtractor` implements `IExtractionService` |
| **Cache** | Redis adapter | `RedisCache` implements `ICacheService` |
| **Export** | PDF/Excel generators | `WeasyPrintPdfGenerator`, `OpenpyxlExcelGenerator` |

```python
# app/infrastructure/repositories/sql_project_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories import IProjectRepository
from app.domain.entities.project import Project
from app.infrastructure.models.project_model import ProjectModel

class SqlProjectRepository(IProjectRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, project_id: str) -> Project | None:
        model = await self._session.get(ProjectModel, project_id)
        return model.to_domain() if model else None

    async def save(self, project: Project) -> None:
        model = ProjectModel.from_domain(project)
        self._session.add(model)
        await self._session.flush()
```

---

## Folder Mapping

```
backend/app/
├── domain/                          # Layer 1 — Domain Core
│   ├── entities/
│   │   ├── project.py
│   │   ├── asset.py
│   │   ├── lease.py
│   │   ├── tenant.py
│   │   ├── assumption_set.py
│   │   ├── valuation_run.py
│   │   ├── cash_flow_line.py
│   │   └── audit_event.py
│   ├── value_objects/
│   │   ├── money.py
│   │   ├── date_range.py
│   │   ├── run_id.py
│   │   └── confidence_score.py
│   ├── services/
│   │   ├── cash_flow_calculator.py
│   │   ├── assumption_validator.py
│   │   └── portfolio_aggregator.py
│   ├── interfaces/
│   │   ├── repositories.py          # Abstract repos (IProjectRepo, etc.)
│   │   ├── file_storage.py          # IFileStorage
│   │   ├── extraction_service.py    # IExtractionService
│   │   ├── cache_service.py         # ICacheService
│   │   └── event_publisher.py       # IEventPublisher
│   ├── events/
│   │   ├── run_completed.py
│   │   ├── assumption_changed.py
│   │   └── lease_approved.py
│   └── exceptions.py
│
├── services/                        # Layer 2 — Application Services
│   ├── project_service.py
│   ├── upload_service.py
│   ├── mapping_service.py
│   ├── extraction_service.py
│   ├── assumption_service.py
│   ├── valuation_run_service.py
│   ├── results_service.py
│   ├── export_service.py
│   └── audit_service.py
│
├── api/                             # Layer 3 — Presentation
│   ├── routes/
│   │   ├── projects.py
│   │   ├── uploads.py
│   │   ├── leases.py
│   │   ├── assumptions.py
│   │   ├── valuation_runs.py
│   │   ├── results.py
│   │   ├── reports.py
│   │   └── audit.py
│   ├── schemas/                     # Pydantic request/response models
│   ├── dependencies.py              # DI wiring
│   └── middleware.py
│
├── infrastructure/                  # Layer 4 — Infrastructure
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── project_model.py
│   │   ├── asset_model.py
│   │   ├── lease_model.py
│   │   └── ...
│   ├── repositories/                # Concrete repo implementations
│   │   ├── sql_project_repository.py
│   │   ├── sql_lease_repository.py
│   │   └── ...
│   ├── storage/
│   │   └── s3_file_storage.py
│   ├── llm/
│   │   ├── azure_openai_extractor.py
│   │   └── claude_extractor.py
│   ├── cache/
│   │   └── redis_cache.py
│   ├── export/
│   │   ├── excel_generator.py
│   │   └── pdf_generator.py
│   └── messaging/
│       └── celery_event_publisher.py
│
├── calculation/                     # DCF Engine (part of Domain, separate for clarity)
│   ├── waterfall.py                 # Core cash flow waterfall
│   ├── indexation.py                # CPI, fixed, capped indexation logic
│   ├── lease_events.py              # Expiry, break, renewal modelling
│   ├── vacancy.py                   # Downtime and re-letting
│   ├── capex.py                     # Capital expenditure scheduling
│   ├── terminal_value.py            # Exit value calculation
│   ├── discounting.py               # PV, NPV, IRR
│   ├── aggregation.py               # Asset → portfolio rollup
│   └── sensitivity.py               # Two-way sensitivity grids
│
└── core/                            # Cross-cutting (config, startup)
    ├── config.py                    # Environment-driven settings
    ├── security.py                  # JWT creation/validation
    └── logging.py                   # Structured logging setup
```

---

## Dependency Rule — What Can Import What

| Layer | Can import from | Cannot import from |
|-------|----------------|--------------------|
| **Domain** | Python stdlib only | Services, API, Infrastructure |
| **Calculation** | Domain value objects | Services, API, Infrastructure, SQLAlchemy |
| **Services** | Domain | API, Infrastructure (uses interfaces only) |
| **API** | Services, Domain schemas | Infrastructure (gets injected) |
| **Infrastructure** | Domain (implements interfaces), Services (receives commands) | API |

### Dependency Injection Wiring

The DI wiring happens in `api/dependencies.py` — this is the only place where infrastructure implementations are connected to domain interfaces:

```python
# app/api/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.interfaces.repositories import IProjectRepository
from app.infrastructure.repositories.sql_project_repository import SqlProjectRepository
from app.services.valuation_run_service import TriggerValuationRunService

async def get_project_repo(session: AsyncSession = Depends(get_session)) -> IProjectRepository:
    return SqlProjectRepository(session)

async def get_run_service(
    project_repo: IProjectRepository = Depends(get_project_repo),
    # ... other deps
) -> TriggerValuationRunService:
    return TriggerValuationRunService(project_repo=project_repo, ...)
```

---

## Testing by Layer

| Layer | Test Type | Database? | Speed |
|-------|-----------|-----------|-------|
| **Domain / Calculation** | Unit tests | No | Fast (ms) |
| **Services** | Unit tests with mocked repos | No | Fast (ms) |
| **API** | Integration tests via TestClient | Optional (can mock) | Medium |
| **Infrastructure** | Integration tests | Yes (testcontainers) | Slow (s) |
| **End-to-End** | Full stack | Yes | Slowest |

The Onion structure means **80%+ of business logic tests run without any database, network, or external service** — just pure Python.
