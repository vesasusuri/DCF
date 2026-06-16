# Testing Strategy

Test types, tools, coverage targets, and the calculation verification approach.

---

## Testing Pyramid

```
         ╱  E2E Tests  ╲          Few, slow, high-confidence
        ╱───────────────╲
       ╱ Integration Tests╲       Medium count, DB/API involved
      ╱─────────────────────╲
     ╱      Unit Tests       ╲    Many, fast, no infrastructure
    ╱─────────────────────────╲
```

| Layer | Count | Speed | Infrastructure | Tool |
|-------|-------|-------|---------------|------|
| Unit | 500+ | < 1ms each | None | pytest |
| Integration | 100+ | < 1s each | PostgreSQL (testcontainers) | pytest + httpx |
| E2E | 20–30 | 5–30s each | Full stack (docker-compose) | Playwright |

---

## Test Categories

### 1. Domain / Calculation Unit Tests

The most critical tests. Pure functions tested without any database or external services.

**Scope:** `app/domain/` and `app/calculation/`

```python
# tests/calculation/test_waterfall.py

def test_simple_lease_cashflow():
    """Single lease, no indexation, 10-year hold."""
    lease = LeaseInput(
        passing_rent=Money(120_000),
        term=DateRange(date(2024, 1, 1), date(2034, 12, 31)),
        indexation_type="none",
    )
    result = calculate_asset_cashflow(
        asset=sample_asset(),
        leases=[lease],
        assumptions=base_assumptions(),
        hold_period_months=120,
    )
    assert result.noi_year_1 == Decimal("120000.00")
    assert result.gav > Decimal("0")


def test_cpi_indexation_compounds_correctly():
    """CPI at 2.5%, threshold 5%, should trigger in year 3."""
    ...


def test_break_option_probability_weighting():
    """50% break probability should blend occupied and vacant CFs."""
    ...
```

**Excel ground truth tests** — the gold standard:

```python
@pytest.mark.parametrize("case", load_excel_test_cases("tests/fixtures/excel/"))
def test_matches_excel_ground_truth(case):
    result = calculate_asset_cashflow(
        asset=case.asset,
        leases=case.leases,
        assumptions=case.assumptions,
        hold_period_months=case.hold_period * 12,
    )
    assert abs(result.gav - case.expected_gav) / case.expected_gav < 0.005  # 0.5% tolerance
    assert abs(result.irr - case.expected_irr) < 0.001  # 0.1pp tolerance
```

### 2. Service Unit Tests

Application services tested with mocked repositories and infrastructure.

```python
# tests/services/test_valuation_run_service.py

async def test_trigger_run_creates_snapshot():
    mock_repo = MockProjectRepository(projects=[sample_project()])
    mock_run_repo = MockRunRepository()
    service = TriggerValuationRunService(mock_repo, mock_run_repo, ...)

    run_id = await service.execute("project-1", "scenario-1", "user-1")

    saved_run = mock_run_repo.saved_runs[0]
    assert saved_run.assumption_snapshot is not None  # Snapshot was frozen
    assert saved_run.status == "queued"
```

### 3. API Integration Tests

FastAPI TestClient with real database (testcontainers).

```python
# tests/api/test_projects_api.py

async def test_create_project(client: AsyncClient, auth_headers: dict):
    response = await client.post("/api/v1/projects", json={
        "name": "Test Portfolio",
        "client": "Test Client",
        "currency": "EUR",
        "valuation_date": "2026-09-30",
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Portfolio"
    assert data["status"] == "draft"
    assert "id" in data
```

### 4. Excel Export Reconciliation Tests

Verify that generated Excel files contain correct values.

```python
# tests/export/test_excel_reconciliation.py

def test_excel_portfolio_summary_matches_run_results(sample_run):
    workbook = generate_excel_workbook(sample_run)
    summary_sheet = workbook["01_Portfolio_Summary"]

    # GAV in Excel must match RunResult.gav
    excel_gav = summary_sheet["B5"].value
    assert abs(excel_gav - sample_run.results.portfolio_gav) < 0.01

    # Every asset row must match individual asset results
    for i, asset_result in enumerate(sample_run.results.assets):
        row = 10 + i
        assert summary_sheet[f"B{row}"].value == asset_result.name
        assert abs(summary_sheet[f"E{row}"].value - asset_result.gav) < 0.01
```

### 5. AI Extraction Evaluation Tests

Track extraction accuracy against a curated evaluation dataset.

```python
# tests/extraction/test_extraction_accuracy.py

@pytest.mark.slow
@pytest.mark.parametrize("doc", load_evaluation_dataset("tests/fixtures/leases/"))
async def test_extraction_accuracy(doc, extractor):
    result = await extractor.extract(doc.parsed_document, LEASE_SCHEMA)

    for field_name, expected in doc.ground_truth.items():
        extracted = result.fields.get(field_name)
        if expected is not None:
            assert extracted is not None, f"Missing field: {field_name}"
            assert extracted.value == expected, f"Wrong value for {field_name}"

# Aggregate accuracy report
def test_overall_extraction_metrics(evaluation_results):
    precision = evaluation_results.precision
    recall = evaluation_results.recall
    f1 = evaluation_results.f1

    assert precision >= 0.85, f"Precision {precision:.2%} below 85% target"
    assert recall >= 0.90, f"Recall {recall:.2%} below 90% target"
```

### 6. E2E Tests (Playwright)

Full user journey tests running against the complete stack.

```typescript
// tests/e2e/full-valuation-flow.spec.ts

test("complete valuation workflow", async ({ page }) => {
  // Login
  await page.goto("/login");
  await page.fill('[name="email"]', "analyst@colliers.de");
  await page.fill('[name="password"]', "test-password");
  await page.click('button[type="submit"]');

  // Create project
  await page.click("text=New Project");
  await page.fill('[name="name"]', "E2E Test Portfolio");
  await page.click("text=Create");

  // Upload file
  await page.click("text=Upload");
  await page.setInputFiles('input[type="file"]', "tests/fixtures/sample_rent_roll.xlsx");
  await page.waitForSelector("text=Upload complete");

  // Map columns and continue through workflow...
  // ...

  // Verify results appear
  await expect(page.locator("[data-testid='gav-value']")).toContainText("€");
});
```

---

## Tools

| Tool | Purpose |
|------|---------|
| **pytest** | Python test runner |
| **pytest-asyncio** | Async test support |
| **pytest-cov** | Coverage reporting |
| **testcontainers** | Disposable PostgreSQL/Redis containers for integration tests |
| **httpx** | Async HTTP client for API tests |
| **factory-boy** | Test data factories |
| **Playwright** | Browser automation for E2E |
| **mypy** | Static type checking (catches bugs before tests) |
| **ruff** | Linting (catches style and correctness issues) |

---

## Coverage Targets

| Scope | Target |
|-------|--------|
| `app/calculation/` | ≥ 95% line coverage |
| `app/domain/` | ≥ 90% line coverage |
| `app/services/` | ≥ 85% line coverage |
| `app/api/` | ≥ 80% line coverage |
| `app/infrastructure/` | ≥ 70% line coverage |
| Overall backend | ≥ 85% line coverage |
| Frontend components | ≥ 70% (critical paths) |

---

## CI Integration

All tests run in GitHub Actions on every push:

```yaml
test-backend:
  services:
    postgres:
      image: postgres:16
      env: { POSTGRES_DB: test, POSTGRES_PASSWORD: test }
    redis:
      image: redis:7
  steps:
    - run: pytest backend/tests/ -x --cov --cov-report=xml
    - uses: codecov/codecov-action@v4

test-frontend:
  steps:
    - run: cd frontend && npm run test -- --coverage

test-e2e:
  # Runs on merge to develop only (slower)
  steps:
    - run: docker-compose -f docker-compose.test.yml up -d
    - run: npx playwright test
```
