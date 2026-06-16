# AI Extraction Pipeline

The AI-powered document ingestion layer. Transforms unstructured files into the controlled valuation data model while maintaining human oversight and auditability.

---

## Operating Principle

**AI proposes, professionals approve.** The extraction pipeline produces structured data with field-level confidence scores. Low-confidence fields and business-critical terms require human review before entering the calculation pipeline.

---

## Pipeline Overview

```
Upload → Classify → Extract → Validate → Score → Review → Approve → Canonical DB
           │            │          │          │         │
           ▼            ▼          ▼          ▼         ▼
      Document      Schema-    Determin-  Confidence  Human-in-
       Type        driven LLM   istic      0–1 per    the-loop
     Detection     Extraction   Rules      field      UI (S04)
```

---

## Stage 1: Document Classification

Automatically identify file type, language, and relevance.

| Input Type | Detection | Canonical Category |
|------------|-----------|-------------------|
| Excel rent roll | File extension + header row analysis | `rent_roll` |
| Lease PDF (German) | LLM classification + language detection | `lease_document` |
| Property fact sheet | LLM + layout analysis | `property_factsheet` |
| Capex schedule | Excel structure + keyword matching | `capex_plan` |
| Market assumptions | LLM + column/field detection | `market_data` |
| Energy certificate | OCR + template matching | `epc_certificate` |
| Unknown | LLM fallback classification | `unclassified` (flagged for review) |

```python
class DocumentClassifier:
    async def classify(self, file: UploadedFile) -> ClassificationResult:
        """
        Returns:
            document_type: str
            language: str (e.g., "de", "en")
            confidence: float (0–1)
            suggested_property: str | None (linked property if detectable)
        """
```

---

## Stage 2: Extraction

### Excel Files — Deterministic Parsing

No LLM needed. Rule-based column mapping.

1. Detect header row (scan first 10 rows for field-name patterns).
2. Auto-map columns to canonical schema using fuzzy matching + known aliases.
3. Handle German-specific formats: date (`DD.MM.YYYY`), numbers (`1.234,56`), currency.
4. Validate totals, detect duplicates, flag ambiguous mappings.
5. Present mapping in S03 (Data Mapping Wizard) for user confirmation.

### PDF Lease Documents — LLM Extraction

Schema-driven extraction using Azure OpenAI GPT-4o or Anthropic Claude.

**Extraction schema (target fields):**

| Category | Fields |
|----------|--------|
| **Tenant** | name, legal_entity, sector, parent_company |
| **Premises** | property_name, address, unit_id, area_sqm, use_type |
| **Term** | lease_start, lease_expiry, break_option_date, extension_option |
| **Rent** | passing_rent, rent_per_sqm, currency, payment_frequency |
| **Indexation** | type (CPI/fixed/capped), rate, base_date, threshold |
| **Incentives** | rent_free_months, stepped_rent_schedule, fit_out_contribution |
| **Obligations** | maintenance_responsibility, insurance, service_charge_cap |
| **Special rights** | subletting_allowed, assignment_clause, purchase_option |

**Prompt architecture:**

```
System: You are a lease abstraction specialist for German commercial real estate.
Extract the following fields from the lease document. For each field, provide:
- value: the extracted value
- confidence: 0.0–1.0 (how certain you are)
- source_page: page number where found
- source_quote: exact quote from the document

Schema: { ... JSON schema of target fields ... }

Important rules:
- Extract amounts in EUR. Convert if stated differently.
- Dates in ISO 8601 format (YYYY-MM-DD).
- If a field is not found, return null with confidence 0.0.
- For ambiguous clauses, extract the most conservative interpretation
  and flag with low confidence.
```

**Extraction process:**

1. Extract native text from PDF (prefer digital text over OCR).
2. For scanned PDFs: run OCR (Tesseract with German language pack).
3. Split into pages, maintain page references.
4. Send to LLM with schema-driven prompt.
5. Parse structured JSON response.
6. Attach source page citations for every extracted field.

```python
class SchemaLeaseExtractor:
    async def extract(
        self,
        document: ParsedDocument,
        schema: ExtractionSchema,
    ) -> ExtractionResult:
        """
        Returns:
            fields: dict[str, ExtractedField]
            Each field has: value, confidence, source_page, source_quote
        """
```

---

## Stage 3: Deterministic Validation

Run outside the LLM — pure rule-based checks that don't depend on AI.

| Check | Rule | Severity |
|-------|------|----------|
| **Mandatory fields** | Tenant, area, rent, lease_start, lease_expiry must be present | Error |
| **Date logic** | lease_start < lease_expiry; break before expiry | Error |
| **Rent plausibility** | Rent per sqm within market range for use_type + region | Warning |
| **Area reconciliation** | Sum of unit areas ≤ total property GLA | Warning |
| **Duplicate detection** | No two leases for same unit with overlapping terms | Error |
| **Currency consistency** | All amounts in same currency within a project | Error |
| **Arithmetic** | Annual rent ≈ monthly rent × 12 (within rounding) | Warning |
| **Indexation validity** | CPI base date in the past; rate > 0 if type is not `none` | Warning |

```python
class DeterministicValidator:
    def validate(self, extracted: ExtractionResult) -> list[ValidationIssue]:
        """
        Returns list of issues, each with:
            field, severity (error/warning/info), message, auto_fixable
        """
```

---

## Stage 4: Confidence Scoring

Each extracted field gets a composite confidence score:

```
Final Confidence = LLM Confidence × Validation Modifier × Source Quality

Where:
  LLM Confidence    = model's self-reported confidence (0–1)
  Validation Modifier = 1.0 if no issues, 0.7 if warnings, 0.3 if errors
  Source Quality     = 1.0 for digital PDF, 0.85 for OCR, 0.7 for poor scan
```

**Thresholds:**

| Score | Action |
|-------|--------|
| ≥ 0.90 | Auto-approvable (but still shown for review) |
| 0.70–0.89 | Requires human review |
| < 0.70 | Flagged as low-confidence; must be manually verified |

---

## Stage 5: Human Review (S04 Screen)

The AI Extraction Review screen presents extracted data alongside the source document.

**UI elements per field:**
- Extracted value (editable)
- Confidence badge (green / yellow / red)
- Source document snippet with highlighted quote
- Page reference (click to jump to source)
- Accept / Edit / Reject buttons
- Reason field (required for edits and rejections)

**Workflow:**
1. Sort fields by confidence (lowest first).
2. Show side-by-side: extracted data table | PDF viewer.
3. User accepts, edits, or rejects each field.
4. All decisions logged to audit trail with timestamp and reason.
5. Once all mandatory fields are approved, data enters canonical DB.

---

## Stage 6: Feedback Loop

Reviewer corrections improve future extraction quality.

```
Correction → Evaluation Dataset → Prompt Refinement → Re-Evaluation

1. Every accept/edit/reject is stored as a training example.
2. Evaluation dataset grows with each project.
3. Periodically re-evaluate extraction prompts against the dataset.
4. Track accuracy metrics over time (precision, recall, F1 per field).
5. Adjust prompts, confidence thresholds, and validation rules.
```

---

## Versioning

| What | Versioned How |
|------|--------------|
| Extraction prompts | Stored in version-controlled YAML files. Prompt version logged per extraction. |
| LLM model | Model deployment name/version logged per extraction. |
| Validation rules | Rule definitions in code, versioned with application. |
| Original source | Immutable copy stored in S3, never modified. |
| Extracted values | Stored with extraction ID, prompt version, model version. |
| Approved values | Final approved value stored separately with reviewer attribution. |

---

## Supported Document Types

| Type | Method | Phase |
|------|--------|-------|
| Excel rent roll | Deterministic parsing + column mapping | Phase 1 |
| Lease PDF (digital, German) | LLM schema-driven extraction | Phase 2 |
| Lease PDF (scanned) | OCR → LLM extraction | Phase 2 |
| Property fact sheet | LLM extraction | Phase 2 |
| Capex schedule (Excel) | Deterministic parsing | Phase 1 |
| Energy certificate | OCR + template matching | Phase 3 |
| Market data (Excel/CSV) | Deterministic parsing | Phase 1 |
| Data room bundles (ZIP) | Auto-classify + route to appropriate extractor | Phase 3 |

---

## Accuracy Targets

| Metric | MVP Target (Phase 2) | Production Target (Phase 4) |
|--------|----------------------|----------------------------|
| Field-level precision | ≥ 85% | ≥ 95% |
| Mandatory field recall | ≥ 90% | ≥ 98% |
| Document classification accuracy | ≥ 95% | ≥ 99% |
| Average review time per lease | < 10 minutes | < 3 minutes |
