# Frontend Architecture

React SPA architecture, screen inventory, component structure, and design system.

---

## Stack

| Technology | Purpose |
|-----------|---------|
| React 18 | UI framework |
| Vite 5 | Build tool and dev server |
| TypeScript 5.4+ | Type safety |
| React Router 6 | Client-side routing |
| Tailwind CSS 3.4 | Utility-first styling |
| shadcn/ui | Accessible, unstyled component primitives |
| React Query (TanStack) | Server state management and caching |
| React Context | Client state (auth, project context) |
| Recharts / Tremor | Charts and data visualisation |
| Zustand (optional) | Complex client state if needed |

---

## Project Structure

```
frontend/src/
├── pages/                        # Route-level page components
│   ├── auth/
│   │   └── Login.tsx             # Login page
│   ├── projects/
│   │   ├── ProjectList.tsx       # S01 — Project Dashboard
│   │   └── ProjectDetail.tsx     # Project wrapper (layout + context)
│   ├── upload/
│   │   └── UploadCentre.tsx      # S02 — Upload Centre
│   ├── mapping/
│   │   └── DataMappingWizard.tsx # S03 — Data Mapping Wizard
│   ├── extraction/
│   │   └── ExtractionReview.tsx  # S04 — AI Extraction Review
│   ├── assumptions/
│   │   └── AssumptionWorkbench.tsx # S05 — Assumption Workbench
│   ├── runs/
│   │   └── RunMonitor.tsx        # S06 — DCF Run Monitor
│   ├── results/
│   │   ├── ValuationResults.tsx  # S07 — Valuation Results
│   │   ├── PortfolioDashboard.tsx # S08 — Portfolio Dashboard
│   │   └── CashFlowDetail.tsx   # C2 — Lease Cash Flow Drill-down
│   ├── reports/
│   │   └── ReportBuilder.tsx     # S10 — Report Builder
│   └── admin/
│       └── AuditLog.tsx          # S11 — Admin & Audit Log
│
├── layouts/
│   ├── AppLayout.tsx             # Main app shell (sidebar + top bar + content)
│   ├── AuthLayout.tsx            # Minimal layout for login/register
│   └── ProjectLayout.tsx         # Project-scoped layout (tabs, breadcrumb)
│
├── components/
│   ├── ui/                       # shadcn/ui base components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Table.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Dialog.tsx
│   │   ├── Badge.tsx
│   │   ├── Tabs.tsx
│   │   └── ...
│   ├── data/                     # Data display components
│   │   ├── DataTable.tsx         # Sortable, filterable table
│   │   ├── KPICard.tsx           # Single metric card
│   │   ├── KPIGrid.tsx           # Grid of KPI cards
│   │   ├── SensitivityHeatmap.tsx
│   │   ├── CashFlowWaterfall.tsx
│   │   └── ValuationBridge.tsx
│   ├── forms/                    # Form components
│   │   ├── AssumptionForm.tsx
│   │   ├── ColumnMapper.tsx
│   │   └── ScenarioSelector.tsx
│   ├── layout/                   # Structural components
│   │   ├── Sidebar.tsx
│   │   ├── TopBar.tsx
│   │   ├── WorkflowStepper.tsx
│   │   └── Breadcrumb.tsx
│   └── feedback/                 # Status indicators
│       ├── ConfidenceBadge.tsx
│       ├── RunProgress.tsx
│       └── ValidationAlert.tsx
│
├── hooks/
│   ├── useAuth.ts                # Auth state and actions
│   ├── useProject.ts             # Current project context
│   ├── useApiQuery.ts            # Typed API query wrapper
│   └── useWebSocket.ts           # Real-time run updates
│
├── lib/
│   ├── api.ts                    # fetchWithAuth() — API client with JWT
│   ├── auth.ts                   # Token management
│   ├── formatters.ts             # Number, currency, date formatting (EUR, DE locale)
│   └── constants.ts              # Route paths, API base URL
│
├── types/
│   ├── project.ts                # Project, Asset, Lease types
│   ├── assumption.ts             # Scenario, AssumptionSet types
│   ├── run.ts                    # ValuationRun, CashFlowLine, RunResult types
│   ├── extraction.ts             # ExtractionResult, ExtractedField types
│   └── api.ts                    # Generic API response types
│
├── App.tsx                       # Root component with providers
├── router.tsx                    # React Router route definitions
└── main.tsx                      # Vite entry point
```

---

## Routing

```tsx
// router.tsx
const router = createBrowserRouter([
  {
    path: "/login",
    element: <AuthLayout />,
    children: [{ index: true, element: <Login /> }],
  },
  {
    path: "/",
    element: <ProtectedRoute><AppLayout /></ProtectedRoute>,
    children: [
      { index: true, element: <Navigate to="/projects" /> },
      { path: "projects", element: <ProjectList /> },
      {
        path: "projects/:projectId",
        element: <ProjectLayout />,
        children: [
          { index: true, element: <Navigate to="upload" /> },
          { path: "upload", element: <UploadCentre /> },
          { path: "mapping/:uploadId", element: <DataMappingWizard /> },
          { path: "extraction/:extractionId", element: <ExtractionReview /> },
          { path: "assumptions", element: <AssumptionWorkbench /> },
          { path: "runs", element: <RunMonitor /> },
          { path: "runs/:runId/results", element: <ValuationResults /> },
          { path: "runs/:runId/portfolio", element: <PortfolioDashboard /> },
          { path: "runs/:runId/cashflow/:assetId", element: <CashFlowDetail /> },
          { path: "reports", element: <ReportBuilder /> },
        ],
      },
      { path: "admin/audit", element: <AuditLog /> },
    ],
  },
]);
```

---

## Screen Inventory

| Screen | Route | Purpose | Phase |
|--------|-------|---------|-------|
| S01 — Project Dashboard | `/projects` | List all projects with status, client, last run | 1 |
| S02 — Upload Centre | `/projects/:id/upload` | Drag-drop file upload, classification, progress | 1 |
| S03 — Data Mapping Wizard | `/projects/:id/mapping/:uid` | Column mapping for Excel rent rolls | 1 |
| S04 — AI Extraction Review | `/projects/:id/extraction/:eid` | Field-level review with source document | 2 |
| S05 — Assumption Workbench | `/projects/:id/assumptions` | Scenario management, global + asset overrides | 1 |
| S06 — DCF Run Monitor | `/projects/:id/runs` | Run queue, progress, errors, recalculation | 1 |
| S07 — Valuation Results | `/projects/:id/runs/:rid/results` | Portfolio KPIs, asset table, sensitivity, drill-down | 1 |
| S08 — Portfolio Dashboard | `/projects/:id/runs/:rid/portfolio` | Interactive charts, value contribution, tenant exposure | 1 |
| C2 — Cash Flow Detail | `/projects/:id/runs/:rid/cashflow/:aid` | Lease-level monthly cash flow table | 2 |
| S10 — Report Builder | `/projects/:id/reports` | PDF/Excel export configuration | 1 |
| S11 — Admin & Audit Log | `/admin/audit` | User management, audit event search | 2 |

---

## App Shell

The main layout follows the wireframe's workflow-driven design:

```
┌─────────────────────────────────────────────────────────────────┐
│ Top Bar: Project Name │ Scenario │ Last Run │ Status │ User    │
├───────────┬─────────────────────────────────────────────────────┤
│           │                                                     │
│ Sidebar   │               Content Area                          │
│           │                                                     │
│ Dashboard │  ┌──────────────────────────────────────────────┐   │
│ Upload    │  │                                              │   │
│ Mapping   │  │        Page content renders here             │   │
│ AI Review │  │                                              │   │
│ Assump-   │  │                                              │   │
│   tions   │  │                                              │   │
│ Run       │  │                                              │   │
│ Results   │  │                                              │   │
│ Portfolio │  │                                              │   │
│ Reports   │  │                                              │   │
│           │  └──────────────────────────────────────────────┘   │
│ ───────── │                                                     │
│ Admin     │                                                     │
└───────────┴─────────────────────────────────────────────────────┘
```

**Sidebar behaviour:**
- Collapsible: 240px expanded, 64px collapsed (icons only).
- Workflow steps shown in order, active step highlighted, completed steps show checkmark.
- AI Review only shown when PDFs are uploaded.

---

## Design System

### Typography

| Level | Font | Size | Weight | Use |
|-------|------|------|--------|-----|
| H1 | Satoshi | 28px | 700 | Page titles |
| H2 | Satoshi | 22px | 600 | Section headers |
| H3 | Satoshi | 18px | 600 | Card titles |
| Body | Satoshi | 14px | 400 | Default text |
| Small | Satoshi | 12px | 400 | Labels, captions |
| Mono | Roboto Mono | 13px | 400 | Numbers, code, IDs |

### Colours

| Token | Hex | Use |
|-------|-----|-----|
| `--primary` | `#1a1a1a` | Headers, primary text |
| `--secondary` | `#6b7280` | Secondary text, labels |
| `--accent` | `#2563eb` | Links, active states, primary buttons |
| `--success` | `#16a34a` | High confidence, approved status |
| `--warning` | `#d97706` | Medium confidence, warnings |
| `--danger` | `#dc2626` | Low confidence, errors, rejected |
| `--surface` | `#ffffff` | Cards, content background |
| `--background` | `#f9fafb` | Page background |
| `--border` | `#e5e7eb` | Dividers, card borders |

### Design Principle

> The UI should always answer three questions: **Where did this number come from?** **Who approved it?** **What happens if I change the assumption?**
