# Reporting & Export

Excel workbook and PDF report generation — both produced from the same canonical valuation run to ensure consistency.

---

## Principle

Every export is linked to a single `run_id`. The run freezes assumptions, data, and model version. Excel and PDF outputs show identical numbers because they read from the same calculated result set.

---

## Excel Workbook Structure

Multi-sheet workbook generated with **openpyxl**. Institutional-grade formatting with named ranges, conditional formatting, and print layouts.

| Sheet | Purpose | Key Content |
|-------|---------|-------------|
| `00_ReadMe` | Methodology & metadata | Model owner, run date, version, source data summary, disclaimers |
| `01_Portfolio_Summary` | High-level KPIs | GAV, NOI, WAULT, occupancy, tenant concentration, sensitivity summary |
| `02_Property_Register` | Asset master data | One row per property: address, GLA, valuation, key assumptions |
| `03_Lease_Register` | Lease details | One row per lease: tenant, unit, rent, term, indexation, approval status |
| `04_Assumptions` | Scenario parameters | Global defaults + asset-level overrides, by period and scenario |
| `05_Cash_Flow_Asset` | Asset-level cash flows | Monthly or annual NOI breakdown by asset |
| `06_Cash_Flow_Lease` | Lease-level cash flows | Detailed lease-level CF for audit and recalculation |
| `07_Valuation_Output` | DCF results | PV, terminal value, yields, IRR, sensitivity tables |
| `08_Data_Quality` | Quality metrics | Missing fields, warnings, overrides, reconciliation status |
| `09_Audit_Log` | Change history | Inputs, changes, approvals, model version, run ID |

### Formatting Standards

- Header row: bold, frozen panes, auto-filter
- Currency cells: `#,##0.00` format, EUR symbol
- Percentage cells: `0.00%` format
- Date cells: `DD.MM.YYYY` (German format)
- Conditional formatting: red for warnings/errors, green for validated
- Named ranges for key outputs (enables downstream Excel models to reference)
- Print area and page breaks configured for each sheet

---

## PDF Report Structure

Institutional investor-grade report generated from HTML templates via **WeasyPrint**.

| Section | Content |
|---------|---------|
| 1. Cover Page | Project name, client, valuation date, Colliers branding |
| 2. Executive Summary | Portfolio value, key risks, recommendation notes |
| 3. Portfolio Overview | Map, asset list, sector mix, regions, size distribution |
| 4. Valuation Methodology | DCF approach, key assumptions, hold period, discount basis |
| 5. DCF Result Summary | GAV, NPV, IRR, yield metrics, valuation bridge chart |
| 6. Cash Flow Charts | NOI timeline, capex schedule, vacancy, terminal value, sensitivity heatmaps |
| 7. Tenant & Lease Analysis | WAULT, expiry profile, top tenants, rent roll vs ERV |
| 8. Asset-by-Asset Pages | Individual property valuation with key metrics (optional photos/maps) |
| 9. Scenario & Sensitivity | Scenario comparison table, 2-way sensitivity grids |
| 10. Data Quality & AI Confidence | Extraction confidence summary, outstanding items |
| 11. Appendices | Detailed cash flows, assumption tables, glossary, source documents |

### PDF Generation Pipeline

```
1. API receives POST /reports/pdf with run_id and template options
2. Load RunResult + CashFlowLines + Assumptions from database
3. Generate charts as SVG/PNG (Matplotlib or chart service)
4. Render HTML from Jinja2 template + data + charts
5. Convert HTML → PDF via WeasyPrint
6. Upload PDF to S3
7. Return download URL
```

---

## Report Builder (S10 Screen)

User-facing configuration screen for export generation.

**Options:**
- Output format: Excel, PDF, or both
- Template: Standard, Executive Summary, Detailed
- Language: German, English
- Sections to include (toggle individual sections)
- Branding: Colliers logo + optional client logo
- Appendix content: include/exclude detailed cash flows
- Scenario: select which scenario(s) to include

---

## Reconciliation

The `08_Data_Quality` sheet and PDF Section 10 ensure transparency:

| Check | Description |
|-------|-------------|
| Source vs Extracted | Original uploaded value vs AI-extracted value |
| Extracted vs Approved | AI extraction vs human-approved value |
| Asset area reconciliation | Sum of unit areas vs total property GLA |
| Rent roll reconciliation | Sum of lease rents vs property-level passing rent |
| Run consistency | Same numbers in Excel and PDF (verified by automated test) |
