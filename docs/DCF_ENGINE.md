# DCF Calculation Engine

The deterministic valuation engine. Pure Python functions — no LLM, no database, no side effects. Every output is reproducible given the same inputs.

---

## Design Principles

1. **Deterministic** — Same inputs always produce same outputs. No randomness, no external API calls.
2. **Pure functions** — No database access, no file I/O. Receives data objects, returns result objects.
3. **Testable** — Every function unit-tested against Excel ground truth.
4. **Versioned** — Engine version stored with every run. Enables reproducibility.
5. **Bottom-up** — Lease → Unit → Asset → Portfolio. Never top-down allocation.

---

## Cash Flow Waterfall

The core calculation builds monthly cash flows bottom-up from each lease:

```
1. Gross Contractual Rent
   └── By lease, unit, and month

2. − Rent-Free Periods & Incentives
   └── Step rents, tenant contributions

3. + Indexation & Uplifts
   └── CPI-linked, fixed, capped/collared

4. − Vacancy & Downtime
   └── After lease expiry or break exercise

5. + Re-letting Income
   └── ERV-based, with downtime and letting costs

6. − Non-Recoverable Operating Expenses
   └── Service charge leakage, management, insurance

7. − Capital Expenditure
   └── Maintenance, landlord works, ESG, TI

8. = Net Operating Income (NOI)

9. + Terminal Value
   └── Stabilised NOI / exit yield − disposal costs

10. = Net Cash Flow

11. → Discount to Present Value
    └── Monthly discounting at scenario discount rate

12. = Gross Asset Value (GAV)
```

---

## Calculation Modules

### `waterfall.py` — Core Cash Flow

Entry point. Orchestrates the full calculation for a single asset.

```python
def calculate_asset_cashflow(
    asset: AssetInput,
    leases: list[LeaseInput],
    assumptions: AssumptionSnapshot,
    hold_period_months: int,
) -> AssetCashFlowResult:
    """
    Calculate monthly cash flows for a single asset.

    Returns:
        AssetCashFlowResult with monthly NOI, terminal value, GAV, yields
    """
```

### `indexation.py` — Rent Indexation Logic

Handles German Light Industrial lease indexation patterns.

| Type | Logic |
|------|-------|
| **CPI-linked** | Compound indexation from base date. Triggered when cumulative CPI change exceeds threshold (typically 5–10%). |
| **Fixed uplift** | Annual or periodic fixed percentage increase. |
| **Capped/collared** | CPI with minimum floor and maximum cap per period. |
| **Delayed indexation** | CPI applied only after initial period (e.g., first 2 years fixed). |
| **Step rent** | Explicit schedule of rent amounts at specific dates. |

```python
def apply_indexation(
    base_rent: Decimal,
    indexation_type: str,
    rate: Decimal,
    base_date: date,
    current_period: date,
    cpi_series: dict[date, Decimal] | None,
    threshold: Decimal | None,
    cap: Decimal | None,
    floor: Decimal | None,
) -> Decimal:
    """Return indexed rent for the given period."""
```

### `lease_events.py` — Lease Event Engine

Models the timeline of lease-level events that affect cash flow.

| Event | Impact |
|-------|--------|
| **Expiry** | Lease income stops; triggers vacancy + re-letting assumptions |
| **Break option** | Probability-weighted: `(1 − P_break) × rent + P_break × vacancy` |
| **Extension option** | Modelled as probability of renewal at adjusted terms |
| **Rent review** | Adjustment to ERV or indexed rent at review date |
| **Rent-free period** | Zero rent for specified months |
| **Stepped rent** | Explicit amount changes per schedule |

```python
def build_lease_timeline(
    lease: LeaseInput,
    assumptions: AssumptionSnapshot,
    start_date: date,
    end_date: date,
) -> list[MonthlyLeaseEvent]:
    """
    Generate month-by-month lease event timeline.
    Each event carries: rent amount, status (occupied/vacant/re-let), confidence.
    """
```

### `vacancy.py` — Vacancy & Re-letting

Models what happens when a lease expires or a break is exercised.

```python
def model_vacancy_period(
    lease_end: date,
    assumptions: AssumptionSnapshot,
    unit: UnitInput,
) -> VacancyResult:
    """
    Returns:
        - downtime_months: void period before re-letting
        - reletting_rent: ERV-based new rent
        - letting_costs: agent fees, incentives
        - tenant_improvement: fit-out contribution
    """
```

### `capex.py` — Capital Expenditure

Schedules and categorises capex items over the hold period.

| Category | Examples |
|----------|---------|
| Maintenance | Roof repair, HVAC replacement, facade |
| Landlord works | Building improvements, common area upgrades |
| Tenant improvements | Fit-out contributions on re-letting |
| ESG / regulatory | Solar PV, insulation, EPC compliance |
| Refurbishment | Major repositioning (vacant possession) |

### `terminal_value.py` — Exit Value Calculation

```python
def calculate_terminal_value(
    stabilised_noi: Decimal,
    exit_yield: Decimal,
    purchaser_costs: Decimal,
    disposal_costs: Decimal,
) -> TerminalValueResult:
    """
    Terminal Value = Stabilised NOI / Exit Yield
    Net Terminal = Terminal Value × (1 − disposal_costs)
    """
```

### `discounting.py` — Present Value

```python
def discount_cashflows(
    monthly_cashflows: list[Decimal],
    annual_discount_rate: Decimal,
) -> list[Decimal]:
    """
    Discount each monthly cash flow to present value.
    Monthly rate = (1 + annual_rate)^(1/12) − 1
    """

def calculate_irr(
    initial_investment: Decimal,
    cashflows: list[Decimal],
    terminal_value: Decimal,
) -> Decimal:
    """Calculate Internal Rate of Return using Newton-Raphson method."""
```

### `aggregation.py` — Portfolio Rollup

```python
def aggregate_portfolio(
    asset_results: list[AssetCashFlowResult],
) -> PortfolioResult:
    """
    Aggregate asset-level results to portfolio level.
    - Sum: GAV, NOI, passing rent, ERV
    - Weighted average: yields, WAULT, WALB (weighted by rent or value)
    - Occupancy: GLA-weighted
    """
```

### `sensitivity.py` — Sensitivity Analysis

```python
def two_way_sensitivity(
    base_result: AssetCashFlowResult | PortfolioResult,
    param_x: str,           # e.g., "discount_rate"
    param_y: str,           # e.g., "exit_yield"
    range_x: list[Decimal], # e.g., [0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08]
    range_y: list[Decimal],
    recalculate_fn: Callable,
) -> SensitivityGrid:
    """
    Produce a 2D sensitivity table showing GAV at each parameter combination.
    """
```

---

## Valuation Outputs

| Output | Definition |
|--------|-----------|
| **Gross Asset Value (GAV)** | PV of operating cash flows + discounted terminal value |
| **Net Present Value (NPV)** | Discounted cash flows after selected costs |
| **Internal Rate of Return (IRR)** | Annualised return from purchase price, CFs, and exit |
| **Initial Yield** | Current NOI / GAV |
| **Reversionary Yield** | ERV-based NOI / GAV |
| **Equivalent Yield** | Single discount rate equating market value to CFs |
| **WAULT** | Weighted average unexpired lease term (by rent) |
| **WALB** | Weighted average lease break (by rent) |
| **Occupancy** | Occupied GLA / total GLA |
| **Passing vs ERV** | Reversion analysis by unit |
| **Sensitivity Grid** | 2-way tables for discount rate × exit yield, ERV × vacancy |

---

## Testing Against Excel Ground Truth

Phase 0 produces 20+ test cases as Excel spreadsheets. The calculation engine must match these within ≤ 0.5% tolerance.

```python
# tests/calculation/test_against_excel.py

@pytest.mark.parametrize("test_case", load_excel_test_cases("tests/fixtures/"))
def test_dcf_matches_excel(test_case):
    result = calculate_asset_cashflow(
        asset=test_case.asset,
        leases=test_case.leases,
        assumptions=test_case.assumptions,
        hold_period_months=test_case.hold_period * 12,
    )
    assert abs(result.gav - test_case.expected_gav) / test_case.expected_gav < 0.005
    assert abs(result.irr - test_case.expected_irr) < 0.001
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Single asset (10 leases, 120 months) | < 100ms |
| 10-asset portfolio | < 2 seconds |
| 100-asset portfolio (1,000 leases) | < 60 seconds |
| Sensitivity grid (7×7 = 49 recalculations) | < 5 seconds per asset |
