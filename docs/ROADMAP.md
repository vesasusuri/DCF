# Implementation Roadmap

Phased delivery plan from discovery to enterprise rollout. Total time to MVP (end of Phase 2): 19–27 weeks.

---

## Timeline Overview

```
Phase 0 ──────────►  Phase 1 ─────────────────►  Phase 2 ─────────────────►  Phase 3 ────────────────────►  Phase 4
Discovery & UX        MVP Core Engine              AI Ingestion Pilot          Portfolio-Scale Beta           Enterprise
3–5 weeks             8–12 weeks                   8–10 weeks                  10–14 weeks                   12+ weeks
                                        ▲
                                        │
                                   MVP Delivery
                                   (end of Phase 2)
```

---

## Phase 0 — Discovery & Foundation

**Duration:** 3–5 weeks  
**Objective:** Validate requirements, produce clickable prototype, establish technical foundation.

### Workstreams

| # | Task | Effort | Deliverable |
|---|------|--------|-------------|
| P0-01 | Stakeholder Interviews & Requirements Gathering | 5–8 days | Validated requirements document |
| P0-02 | Secure Pilot Portfolio Data | 2–3 days | Anonymised sample dataset |
| P0-03 | Sample Data Analysis & Data Dictionary | 3–4 days | Data dictionary v1 |
| P0-04 | DCF Methodology Validation & Test Cases | 4–5 days | Excel ground truth + 20 test cases |
| P0-05 | Assumption Taxonomy & Default Values | 3–4 days | Assumption schema + defaults |
| P0-06 | Clickable UX Prototype | 5–7 days | Interactive Figma prototype |
| P0-07 | User Testing & Prototype Iteration | 3–4 days | Iterated prototype + findings |
| P0-08 | Technology Stack Decision & Architecture Document | 3–5 days | ADR + architecture diagrams |
| P0-09 | Database Schema Design | 3–5 days | Alembic migrations + ER diagram |
| P0-10 | Dev Environment & CI/CD Setup | 3–4 days | docker-compose + GitHub Actions |
| P0-11 | API Design & Contract Definition | 4–5 days | OpenAPI spec + mock server |
| P0-12 | AI Extraction Feasibility Experiments | 5–7 days | Feasibility report + accuracy metrics |
| P0-13 | Implementation Backlog Creation | 2–3 days | Prioritised Jira/Linear backlog |
| P0-14 | Phase 0 Gate Review | 1–2 days | Go/no-go decision |

**Gate criteria:** Prototype validated, test cases approved, architecture signed off, pilot data secured.

---

## Phase 1 — MVP Core Engine

**Duration:** 8–12 weeks  
**Objective:** Working platform for 5–10 assets with manual data entry, DCF calculation, and export.

### Workstreams

**D: Backend & Database**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P1-01 | Core API Scaffolding & Authentication | 4–5 days | P0-10 |
| P1-02 | Project & Asset CRUD API | 3–4 days | P1-01 |
| P1-03 | File Upload & Storage Service | 3–4 days | P1-01 |
| P1-04 | Excel Parsing & Data Mapping Engine | 5–6 days | P1-03 |
| P1-05 | Assumption Management API | 5–6 days | P1-02 |

**E: Calculation Engine**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P1-06 | Cash Flow Waterfall — Core Logic | 6–8 days | P0-04 |
| P1-07 | Lease Event Engine | 4–5 days | P1-06 |
| P1-08 | Asset & Portfolio Aggregation | 4–5 days | P1-06 |
| P1-09 | Valuation Run Orchestrator | 5–6 days | P1-06 |
| P1-10 | Results API & Data Access Layer | 3–4 days | P1-09 |

**F: Frontend**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P1-11 | App Shell & Navigation Framework | 4–5 days | P0-06, P1-01 |
| P1-12 | S01 — Project Dashboard Screen | 2–3 days | P1-11 |
| P1-13 | S02 — Upload Centre Screen | 3–4 days | P1-11, P1-03 |
| P1-14 | S03 — Data Mapping Wizard Screen | 4–5 days | P1-11, P1-04 |
| P1-15 | S05 — Assumption Workbench Screen | 5–6 days | P1-11, P1-05 |
| P1-16 | S06 — DCF Run Monitor Screen | 3–4 days | P1-11, P1-09 |
| P1-17 | S07 — Valuation Results Screen | 6–7 days | P1-11, P1-10 |
| P1-18 | S08 — Portfolio Dashboard Screen | 4–5 days | P1-17 |

**G: Reports & Testing**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P1-19 | Excel Workbook Export Engine | 5–6 days | P1-10 |
| P1-20 | PDF Report Export Engine | 4–5 days | P1-10 |
| P1-21 | S10 — Report Builder Screen (Basic) | 3–4 days | P1-11, P1-19 |
| P1-22 | Excel Reconciliation Testing | 3–4 days | P1-19 |
| P1-23 | End-to-End Integration Testing | 4–5 days | all P1 tasks |
| P1-24 | Performance Baseline & Optimization | 3–4 days | P1-23 |
| P1-25 | Staging Deployment & User Acceptance | 3–4 days | P1-23 |
| P1-26 | Phase 1 Gate Review | 2 days | P1-25 |

**Gate criteria:** 5–10 asset portfolio calculated correctly (matches Excel ground truth), exports verified, stakeholders accept.

---

## Phase 2 — AI Ingestion & MVP Completion

**Duration:** 8–10 weeks  
**Objective:** AI lease extraction, audit trail, quality assurance, pilot validation.

### Workstreams

**I: AI Extraction**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P2-01 | Document Classification Service | 3–4 days | P1-03 |
| P2-02 | Schema-Driven Lease Extraction Engine | 7–9 days | P2-01 |
| P2-03 | Cross-Document Reconciliation | 4–5 days | P2-02 |
| P2-04 | S04 — AI Extraction Review Screen | 5–6 days | P1-11, P2-02 |
| P2-05 | Extraction Feedback Loop | 4–5 days | P2-04 |

**J: Audit & Quality**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P2-06 | Immutable Audit Log Service | 5–6 days | P1-01 |
| P2-07 | S11 — Admin & Audit Log Viewer (Basic) | 3–4 days | P2-06 |
| P2-08 | Data Quality Dashboard | 4–5 days | P1-11, P2-02 |
| P2-09 | Enhanced Validation Engine | 4–5 days | P1-04, P2-02 |

**K: Hardening**

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| P2-10 | C2 — Lease Cash Flow Detail Screen | 3–4 days | P1-17 |
| P2-11 | Sensitivity Table on Results Screen | 3–4 days | P1-17 |
| P2-12 | Report Enhancements — AI Confidence Sections | 2–3 days | P1-20, P2-02 |
| P2-13 | Automated Calculation Test Suite | 5–6 days | P1-06 |
| P2-14 | AI Extraction Evaluation Dataset & Metrics | 4–5 days | P2-02 |
| P2-15 | Security Hardening — MVP Level | 4–5 days | all |
| P2-16 | Error Handling & UX Polish | 3–4 days | all frontend |
| P2-17 | Full E2E Testing with AI Pipeline | 4–5 days | all P2 |
| P2-18 | Pilot Validation with Colliers Team | 4–5 days | P2-17 |
| P2-19 | MVP Acceptance Criteria Verification | 3–4 days | P2-18 |
| P2-20 | MVP Gate Review & Sign-Off | 2 days | P2-19 |

**Gate criteria (MVP Acceptance — 10 items):**
1. ≥ 10 assets / 100 leases processed in a single project
2. DCF values match Excel ground truth within ≤ 0.5%
3. AI extraction accuracy ≥ 85% on pilot lease PDFs
4. Complete audit trail for every data change
5. Excel workbook and PDF report generated from same run
6. Sensitivity analysis (2-way grid) functional
7. All critical/high-severity bugs resolved
8. Staging environment stable for 2+ weeks
9. Colliers valuation team completes pilot validation
10. Security review completed (auth, encryption, access control)

---

## Phase 3 — Portfolio-Scale Beta (Post-MVP)

**Duration:** 10–14 weeks  
**Scope:** Batch calculation for 100-asset portfolios, scenario engine, role permissions, SSO integration, advanced dashboards.

## Phase 4 — Enterprise Rollout (Post-MVP)

**Duration:** 12+ weeks  
**Scope:** Security hardening, client portal, third-party integrations, governance documentation, SLA, training, operating model.

---

## Critical Path

The longest sequential dependency chain determines the minimum timeline:

```
P0-04 (DCF test cases)
  → P1-06 (Cash flow waterfall)
    → P1-07 (Lease events)
      → P1-09 (Run orchestrator)
        → P1-10 (Results API)
          → P1-17 (Results screen)
            → P1-19 (Excel export)
              → P1-22 (Reconciliation testing)
                → P1-23 (E2E testing)
                  → P2-17 (Full E2E with AI)
                    → P2-18 (Pilot validation)
                      → P2-19 (MVP acceptance)
```

**19 tasks on critical path.** Any delay here delays the entire project.
