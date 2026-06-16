# Data Model

Core entities, relationships, and schema design for the AI-DCF Valuation Platform.

---

## Entity Relationship Overview

```
Organisation
    │
    └── Project (1:N)
          │
          ├── Portfolio (1:N)
          │     └── Property / Asset (N:M)
          │           ├── Unit (1:N)
          │           │     └── Lease (1:N)
          │           │           └── Tenant (N:1)
          │           └── CapexItem (1:N)
          │
          ├── AssumptionSet / Scenario (1:N)
          │     └── AssumptionOverride (1:N)
          │
          ├── Upload / SourceFile (1:N)
          │     └── ExtractionResult (1:N)
          │
          ├── ValuationRun (1:N)
          │     ├── CashFlowLine (1:N)
          │     ├── RunResult (1:N)
          │     └── Report (1:N)
          │
          └── AuditEvent (1:N)
```

---

## Core Entities

### Organisation

The top-level tenant. Represents a Colliers team, client, or investor entity.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | VARCHAR(255) | Organisation name |
| `type` | ENUM | `colliers_team`, `client`, `investor` |
| `jurisdiction` | VARCHAR(10) | Country code (e.g., `DE`) |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `permissions` | JSONB | Organisation-level settings |

### Project

A valuation mandate or portfolio analysis project. Central organising entity.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `organisation_id` | UUID (FK) | Owning organisation |
| `name` | VARCHAR(255) | Project name |
| `client` | VARCHAR(255) | Client name |
| `currency` | VARCHAR(3) | `EUR` (default) |
| `valuation_date` | DATE | Effective valuation date |
| `status` | ENUM | `draft`, `data_collection`, `review`, `calculation`, `completed`, `archived` |
| `created_by` | UUID (FK) | User who created |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

### Property (Asset)

Individual real estate asset within a portfolio.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `project_id` | UUID (FK) | Parent project |
| `name` | VARCHAR(255) | Property name |
| `address` | TEXT | Full address |
| `city` | VARCHAR(100) | City |
| `postal_code` | VARCHAR(10) | |
| `state` | VARCHAR(50) | Bundesland |
| `country` | VARCHAR(3) | `DE` |
| `latitude` | DECIMAL(9,6) | Geocode |
| `longitude` | DECIMAL(9,6) | Geocode |
| `asset_type` | ENUM | `warehouse`, `production`, `logistics`, `mixed_use`, `urban_logistics`, `office_ancillary` |
| `gla_sqm` | DECIMAL(12,2) | Gross leasable area (m²) |
| `site_area_sqm` | DECIMAL(12,2) | Total site area (m²) |
| `year_built` | INTEGER | Year of construction |
| `year_renovated` | INTEGER | Last renovation |
| `epc_rating` | VARCHAR(10) | Energy Performance Certificate |
| `occupancy_rate` | DECIMAL(5,4) | Current occupancy (0–1) |
| `metadata` | JSONB | Flexible additional fields |

### Unit

Lettable space component within a property. Supports multi-tenant and mixed-use assets.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `property_id` | UUID (FK) | Parent property |
| `name` | VARCHAR(100) | Unit identifier (e.g., "Halle A", "Büro 2.OG") |
| `use_type` | ENUM | `warehouse`, `production`, `office`, `yard`, `parking`, `mezzanine`, `other` |
| `area_sqm` | DECIMAL(10,2) | Lettable area (m²) |
| `specification` | JSONB | Height, loading docks, power, etc. |

### Lease

Contractual agreement between tenant and property owner. Core input for DCF calculation.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `unit_id` | UUID (FK) | Leased unit |
| `tenant_id` | UUID (FK) | Tenant entity |
| `lease_start` | DATE | Lease commencement |
| `lease_expiry` | DATE | Contractual expiry |
| `break_option_date` | DATE | Earliest break option |
| `break_exercise_probability` | DECIMAL(5,4) | 0–1, used in DCF modelling |
| `extension_option` | BOOLEAN | Renewal option exists |
| `passing_rent_annual` | DECIMAL(14,2) | Current annual rent (EUR) |
| `passing_rent_sqm_month` | DECIMAL(8,2) | Rent per m² per month |
| `rent_free_months` | INTEGER | Remaining rent-free period |
| `stepped_rent_schedule` | JSONB | Array of `{date, amount}` for step rents |
| `indexation_type` | ENUM | `cpi`, `fixed`, `capped_collar`, `none` |
| `indexation_rate` | DECIMAL(5,4) | Fixed rate or cap/collar bounds |
| `indexation_base_date` | DATE | Reference date for CPI |
| `indexation_threshold` | DECIMAL(5,4) | Minimum CPI change to trigger |
| `incentives` | JSONB | Fit-out contributions, rent-free details |
| `source` | ENUM | `excel_upload`, `ai_extraction`, `manual_entry` |
| `confidence_score` | DECIMAL(3,2) | AI confidence (0–1), NULL if manual |
| `approved` | BOOLEAN | Human-approved for calculation |
| `approved_by` | UUID (FK) | Approving user |
| `approved_at` | TIMESTAMPTZ | |

### Tenant

Tenant master data, shared across leases.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | VARCHAR(255) | Tenant name |
| `sector` | VARCHAR(100) | Industry sector |
| `covenant_rating` | ENUM | `strong`, `medium`, `weak`, `unknown` |
| `group_name` | VARCHAR(255) | Parent company (if applicable) |

### AssumptionSet (Scenario)

Scenario-specific valuation assumptions. Supports base, upside, downside, and custom scenarios.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `project_id` | UUID (FK) | Parent project |
| `name` | VARCHAR(255) | Scenario name (e.g., "Base Case", "Downside") |
| `parent_id` | UUID (FK) | Cloned-from scenario (for tracking lineage) |
| `global_defaults` | JSONB | Portfolio-wide assumption defaults |
| `created_by` | UUID (FK) | |
| `created_at` | TIMESTAMPTZ | |

**`global_defaults` JSONB structure:**
```json
{
  "discount_rate": 0.065,
  "exit_yield": 0.055,
  "erv_growth_pa": 0.02,
  "vacancy_rate": 0.05,
  "vacancy_downtime_months": 6,
  "reletting_costs_months": 3,
  "capex_per_sqm_pa": 5.00,
  "inflation_rate": 0.025,
  "hold_period_years": 10,
  "purchaser_costs": 0.075,
  "disposal_costs": 0.015
}
```

### AssumptionOverride

Per-asset or per-unit overrides to the scenario defaults.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `assumption_set_id` | UUID (FK) | Parent scenario |
| `scope` | ENUM | `property`, `unit`, `use_type` |
| `scope_id` | UUID | Property or unit ID |
| `field` | VARCHAR(100) | e.g., `discount_rate`, `erv_growth_pa` |
| `value` | DECIMAL(14,6) | Override value |
| `reason` | TEXT | Why this override was made |
| `set_by` | UUID (FK) | User |
| `set_at` | TIMESTAMPTZ | |

### ValuationRun

Immutable record of a DCF calculation execution. The Run-ID principle.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Run-ID (primary key) |
| `project_id` | UUID (FK) | Parent project |
| `assumption_set_id` | UUID (FK) | Frozen scenario |
| `assumption_snapshot` | JSONB | Complete assumption state at run time |
| `model_version` | VARCHAR(20) | Calculation engine version (semver) |
| `status` | ENUM | `queued`, `running`, `completed`, `failed` |
| `triggered_by` | UUID (FK) | User who triggered |
| `started_at` | TIMESTAMPTZ | |
| `completed_at` | TIMESTAMPTZ | |
| `total_assets` | INTEGER | |
| `total_leases` | INTEGER | |
| `error_log` | JSONB | Any warnings or errors |

### CashFlowLine

Time-series line items produced by the DCF engine. One row per period × asset × line type.

| Field | Type | Description |
|-------|------|-------------|
| `id` | BIGINT | Auto-increment |
| `run_id` | UUID (FK) | Parent valuation run |
| `property_id` | UUID (FK) | Asset |
| `lease_id` | UUID (FK) | Lease (NULL for property-level items) |
| `period` | DATE | Month start date |
| `line_type` | ENUM | `gross_rent`, `vacancy`, `opex`, `capex`, `noi`, `terminal_value`, etc. |
| `amount` | DECIMAL(16,2) | EUR |
| `scenario` | VARCHAR(100) | Scenario reference |

**Indexed on:** `(run_id, property_id, period)` and `(run_id, line_type)`.

### RunResult

Aggregated valuation outputs per asset and portfolio level.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `run_id` | UUID (FK) | Parent run |
| `scope` | ENUM | `property`, `portfolio` |
| `property_id` | UUID (FK) | NULL for portfolio-level |
| `gav` | DECIMAL(16,2) | Gross Asset Value |
| `npv` | DECIMAL(16,2) | Net Present Value |
| `irr` | DECIMAL(8,6) | Internal Rate of Return |
| `initial_yield` | DECIMAL(8,6) | |
| `reversionary_yield` | DECIMAL(8,6) | |
| `equivalent_yield` | DECIMAL(8,6) | |
| `wault_years` | DECIMAL(6,2) | Weighted Average Unexpired Lease Term |
| `walb_years` | DECIMAL(6,2) | Weighted Average Lease Break |
| `occupancy_rate` | DECIMAL(5,4) | |
| `passing_rent_total` | DECIMAL(14,2) | |
| `erv_total` | DECIMAL(14,2) | |
| `sensitivity_grid` | JSONB | Pre-computed 2-way sensitivity table |

### AuditEvent

Append-only log of every data mutation. Immutable by design.

| Field | Type | Description |
|-------|------|-------------|
| `id` | BIGINT | Auto-increment (GENERATED ALWAYS) |
| `project_id` | UUID (FK) | Scope |
| `entity_type` | VARCHAR(50) | e.g., `lease`, `assumption`, `run` |
| `entity_id` | UUID | ID of changed entity |
| `action` | ENUM | `create`, `update`, `delete`, `approve`, `reject`, `trigger_run` |
| `field` | VARCHAR(100) | Changed field (NULL for create/delete) |
| `old_value` | TEXT | Previous value |
| `new_value` | TEXT | New value |
| `reason` | TEXT | User-provided reason |
| `user_id` | UUID (FK) | Who made the change |
| `timestamp` | TIMESTAMPTZ | When (server time) |
| `ip_address` | INET | Client IP |

**Constraints:** No UPDATE or DELETE allowed on this table. Enforced at the database level.

---

## Schema Separation

Following the concept doc's recommendation, data is separated into schemas reflecting its lifecycle stage:

| Schema | Purpose | Example Tables |
|--------|---------|---------------|
| `source` | Raw uploaded data, before any processing | `source_files`, `raw_excel_rows` |
| `extracted` | AI-extracted data awaiting human review | `extracted_leases`, `extraction_confidence` |
| `approved` | Human-reviewed, canonical data used for calculation | `properties`, `leases`, `assumptions` |
| `calculated` | Immutable calculation outputs linked to run-ID | `valuation_runs`, `cash_flow_lines`, `run_results` |
| `audit` | Append-only event log | `audit_events` |

---

## Indexes

Key performance indexes for common query patterns:

```sql
-- Fast project listing by org
CREATE INDEX idx_project_org ON approved.projects(organisation_id, status);

-- Fast lease lookup for DCF calculation
CREATE INDEX idx_lease_unit ON approved.leases(unit_id) WHERE approved = true;

-- Cash flow time-series queries
CREATE INDEX idx_cashflow_run_period ON calculated.cash_flow_lines(run_id, period);
CREATE INDEX idx_cashflow_run_type ON calculated.cash_flow_lines(run_id, line_type);

-- Audit log searches
CREATE INDEX idx_audit_project_time ON audit.audit_events(project_id, timestamp DESC);
CREATE INDEX idx_audit_entity ON audit.audit_events(entity_type, entity_id);
```
