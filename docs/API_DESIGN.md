# API Design

RESTful API structure, endpoint conventions, authentication, and error handling.

---

## Conventions

| Aspect | Convention |
|--------|-----------|
| Format | JSON (request and response) |
| Naming | snake_case for fields |
| Versioning | URL prefix: `/api/v1/` |
| Pagination | `?page=1&page_size=50` → `{ items: [], total: N, page: N, page_size: N }` |
| Sorting | `?sort_by=created_at&order=desc` |
| Filtering | Query params: `?status=active&asset_type=warehouse` |
| Dates | ISO 8601: `2026-06-15T10:30:00Z` |
| Money | Decimal strings with 2dp: `"1234567.89"` |
| IDs | UUIDs: `"a1b2c3d4-e5f6-..."` |
| Auth | `Authorization: Bearer <JWT>` |
| Errors | Structured: `{ "error": { "code": "...", "message": "...", "details": [...] } }` |

---

## Authentication

### Login

```
POST /api/v1/auth/login
Body: { "email": "...", "password": "..." }
→ 200: { "access_token": "...", "refresh_token": "...", "expires_in": 1800 }
```

### Refresh

```
POST /api/v1/auth/refresh
Body: { "refresh_token": "..." }
→ 200: { "access_token": "...", "expires_in": 1800 }
```

### Current User

```
GET /api/v1/auth/me
→ 200: { "id": "...", "email": "...", "name": "...", "role": "...", "organisation_id": "..." }
```

---

## Endpoints by Domain

### Projects

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/projects` | Create a valuation project |
| `GET` | `/api/v1/projects` | List projects (paginated, filtered by org) |
| `GET` | `/api/v1/projects/{id}` | Get project details |
| `PATCH` | `/api/v1/projects/{id}` | Update project metadata |
| `DELETE` | `/api/v1/projects/{id}` | Archive project (soft delete) |

### Uploads / Files

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/projects/{id}/uploads` | Upload files (multipart), start classification |
| `GET` | `/api/v1/projects/{id}/uploads` | List uploaded files with status |
| `GET` | `/api/v1/uploads/{id}/preview` | Preview parsed content |
| `DELETE` | `/api/v1/uploads/{id}` | Remove an uploaded file |

### Data Mapping (Excel)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/uploads/{id}/columns` | Get detected columns from Excel |
| `POST` | `/api/v1/uploads/{id}/mapping` | Submit column mapping to canonical schema |
| `GET` | `/api/v1/uploads/{id}/mapping/preview` | Preview mapped data before confirmation |
| `POST` | `/api/v1/uploads/{id}/mapping/confirm` | Confirm mapping and import to approved schema |

### AI Extraction

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/projects/{id}/extract` | Start AI extraction for selected files |
| `GET` | `/api/v1/extractions/{id}` | Get extraction results with confidence scores |
| `PATCH` | `/api/v1/extractions/{id}/fields/{field}` | Accept / edit / reject an extracted field |
| `POST` | `/api/v1/extractions/{id}/approve-all` | Approve all high-confidence fields |

### Properties (Assets)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/projects/{id}/properties` | List properties in project |
| `GET` | `/api/v1/properties/{id}` | Get property details with units and leases |
| `PATCH` | `/api/v1/properties/{id}` | Update property fields |
| `POST` | `/api/v1/projects/{id}/properties` | Manually create a property |

### Leases

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/properties/{id}/leases` | List leases for a property |
| `GET` | `/api/v1/leases/{id}` | Get lease detail |
| `PATCH` | `/api/v1/leases/{id}` | Edit lease fields (triggers audit event) |
| `POST` | `/api/v1/leases/{id}/approve` | Approve lease data for calculation |

### Assumptions / Scenarios

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/projects/{id}/scenarios` | List scenarios |
| `POST` | `/api/v1/projects/{id}/scenarios` | Create scenario (or clone from existing) |
| `GET` | `/api/v1/scenarios/{id}` | Get scenario with global defaults + overrides |
| `PATCH` | `/api/v1/scenarios/{id}` | Update global defaults |
| `POST` | `/api/v1/scenarios/{id}/overrides` | Add asset-level override |
| `DELETE` | `/api/v1/scenarios/{id}/overrides/{oid}` | Remove override |

### Valuation Runs

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/valuation-runs` | Trigger DCF calculation |
| `GET` | `/api/v1/valuation-runs/{id}` | Get run status and summary |
| `GET` | `/api/v1/valuation-runs/{id}/results` | Get valuation results (GAV, NPV, IRR, etc.) |
| `GET` | `/api/v1/valuation-runs/{id}/cashflows` | Get detailed cash flow lines (paginated) |
| `GET` | `/api/v1/valuation-runs/{id}/sensitivity` | Get sensitivity grid |
| `GET` | `/api/v1/projects/{id}/runs` | List all runs for a project |
| `GET` | `/api/v1/valuation-runs/{id}/compare/{other_id}` | Compare two runs |

### Reports / Export

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/reports/excel` | Generate Excel workbook from run |
| `POST` | `/api/v1/reports/pdf` | Generate PDF report from run |
| `GET` | `/api/v1/reports/{id}` | Get report metadata and download URL |
| `GET` | `/api/v1/reports/{id}/download` | Download report file (presigned URL redirect) |

### Audit Log

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/projects/{id}/audit` | Search audit events (paginated, filtered) |
| `GET` | `/api/v1/audit/{event_id}` | Get single audit event detail |

---

## Request / Response Examples

### Create Project

```http
POST /api/v1/projects
Authorization: Bearer eyJhbGci...

{
  "name": "Colliers LI Portfolio Q3 2026",
  "client": "Investor ABC",
  "currency": "EUR",
  "valuation_date": "2026-09-30"
}
```

```json
// 201 Created
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Colliers LI Portfolio Q3 2026",
  "client": "Investor ABC",
  "currency": "EUR",
  "valuation_date": "2026-09-30",
  "status": "draft",
  "created_by": "user-uuid",
  "created_at": "2026-06-15T14:30:00Z"
}
```

### Trigger Valuation Run

```http
POST /api/v1/valuation-runs
Authorization: Bearer eyJhbGci...

{
  "project_id": "a1b2c3d4-...",
  "scenario_id": "base-case-uuid",
  "assets": "all"
}
```

```json
// 202 Accepted
{
  "run_id": "run-uuid",
  "status": "queued",
  "total_assets": 15,
  "total_leases": 142,
  "model_version": "1.2.0"
}
```

---

## Error Responses

```json
// 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "valuation_date", "message": "Must be a future date" },
      { "field": "currency", "message": "Must be ISO 4217 code" }
    ]
  }
}

// 404 Not Found
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project a1b2c3d4-... does not exist"
  }
}

// 409 Conflict
{
  "error": {
    "code": "RUN_IN_PROGRESS",
    "message": "A valuation run is already in progress for this project"
  }
}
```
