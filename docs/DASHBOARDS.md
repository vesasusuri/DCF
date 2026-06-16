# Dashboards & Data Warehouse

Dashboard specifications, KPIs, and the semantic data layer between the valuation database and the BI/visualisation frontend.

---

## Principle

Dashboards are not a static copy of the report. They help users **explore** the portfolio, **identify risks**, **review assumptions**, and **explain value drivers**. A semantic data layer sits between the valuation database and the dashboard components.

---

## Dashboard Inventory

### 1. Portfolio Command Centre (S08)

The primary portfolio-level view after a valuation run.

| KPI | Calculation | Visualisation |
|-----|-------------|---------------|
| Gross Asset Value (GAV) | Sum of asset GAVs | Large number + trend |
| Net Operating Income | Sum of asset NOIs | Large number |
| WAULT | Rent-weighted avg unexpired term | Number + distribution chart |
| Occupancy | GLA-weighted occupancy | Percentage + bar |
| Top 5 tenants | By rent contribution | Horizontal bar chart |
| Value by asset type | GAV grouped by use_type | Donut / pie chart |
| Value by region | GAV grouped by city/state | Map or treemap |
| Run status | Latest run metadata | Status badge |
| Data quality score | % fields validated, no errors | Score + breakdown |

### 2. Asset Explorer

Property-level cards for drill-down analysis.

| Element | Content |
|---------|---------|
| Property card | Name, address, photo placeholder, GLA, occupancy, GAV, passing rent |
| Asset ranking | Table sorted by GAV, yield, ERV gap, capex exposure |
| Valuation per sqm | Bar chart comparing assets |
| Map view | Geocoded properties on map with value-sized markers |

### 3. Lease Event Dashboard

Timeline-based view of upcoming lease events.

| Visualisation | Data |
|---------------|------|
| Expiry calendar | Stacked bar chart by year — expiring rent |
| Break option timeline | Breaks within next 24 months, probability-weighted |
| Rent review dates | Upcoming reviews with current vs ERV gap |
| Re-letting risk | Assets with highest vacancy risk (by rent at risk) |
| Tenant roll-over | Which tenants are likely to renew vs vacate |

### 4. Sensitivity Dashboard

Interactive what-if analysis.

| Visualisation | Inputs |
|---------------|--------|
| 2-way heatmap | Discount rate × exit yield → GAV |
| Tornado chart | Single-variable impact ranking (which assumption moves GAV most?) |
| Scenario comparison | Base vs upside vs downside — side-by-side KPIs |
| Value-at-risk | Portfolio drawdown under stress scenarios |

### 5. Tenant Exposure Dashboard

Concentration risk analysis.

| Metric | Visualisation |
|--------|---------------|
| Top 10 tenants by rent | Horizontal bar |
| Sector concentration | Donut chart |
| Covenant quality distribution | Stacked bar (strong/medium/weak) |
| Geographic concentration | Map or treemap by state/city |
| Single-tenant risk | Assets with ≥ 80% rent from one tenant |

### 6. Capex & ESG Dashboard

Capital expenditure planning and sustainability.

| Metric | Visualisation |
|--------|---------------|
| Capex timeline | Stacked area chart by year and category |
| Category split | Donut: maintenance vs TI vs ESG vs refurb |
| ESG capex impact | Effect on rent assumptions and yield |
| EPC rating distribution | Bar chart across portfolio |

### 7. Data Quality Dashboard

Extraction confidence and data completeness.

| Metric | Visualisation |
|--------|---------------|
| Overall quality score | Percentage (fields validated / total fields) |
| Extraction confidence | Distribution histogram |
| Missing fields | List with severity |
| Unresolved conflicts | Count + drill-down |
| Review progress | % reviewed vs pending |

---

## Semantic Data Layer

A lightweight KPI layer sits between the database and dashboard components. This prevents ad-hoc metric definitions and ensures consistency between dashboards and reports.

```python
# lib/kpi_definitions.py — Single source of truth for KPI calculations

KPI_REGISTRY = {
    "gav": {
        "label": "Gross Asset Value",
        "unit": "EUR",
        "format": "#,##0",
        "query": "SELECT SUM(gav) FROM run_results WHERE run_id = :run_id AND scope = 'property'",
        "description": "Sum of discounted cash flows and terminal values across all assets.",
    },
    "wault": {
        "label": "WAULT (years)",
        "unit": "years",
        "format": "0.0",
        "aggregation": "rent_weighted_average",
        "description": "Weighted average unexpired lease term, weighted by passing rent.",
    },
    # ... etc.
}
```

**Frontend usage:**

```tsx
// components/data/KPICard.tsx
<KPICard
  metric="gav"
  value={runResult.gav}
  previousValue={previousRun?.gav}  // Shows trend arrow
  format="currency"
/>
```

---

## Chart Technology

| Chart Type | Library | Used In |
|------------|---------|---------|
| KPI cards with trend | Tremor `Card` + `Metric` | Portfolio dashboard |
| Bar / stacked bar | Recharts `BarChart` | Lease events, tenant exposure |
| Line / area | Recharts `AreaChart` | Cash flow timeline |
| Donut / pie | Recharts `PieChart` | Sector mix, value by type |
| Heatmap | Custom Recharts or D3 | Sensitivity grid |
| Waterfall | Custom Recharts | Valuation bridge |
| Table with sorting | shadcn/ui `DataTable` | Asset register, lease register |
| Map | Mapbox GL or Leaflet | Property locations |

---

## Real-Time Updates

During active valuation runs, dashboards update via polling or WebSocket:

```
Run triggered → Worker processes assets one by one
  → Each asset completion emits progress event
    → Frontend polls /runs/{id} every 5s (or WebSocket push)
      → Progress bar updates: "12/45 assets calculated"
      → Partial results appear as assets complete
```
