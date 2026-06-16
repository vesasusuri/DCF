import { createBrowserRouter, Navigate } from 'react-router-dom'

import { AppLayout } from './layouts/AppLayout'
import { AuthLayout } from './layouts/AuthLayout'
import { ProjectLayout } from './layouts/ProjectLayout'
import { AuditLog } from './pages/admin/AuditLog'
import { Login } from './pages/auth/Login'
import { AssumptionWorkbench } from './pages/assumptions/AssumptionWorkbench'
import { ExtractionReview } from './pages/extraction/ExtractionReview'
import { DataMappingWizard } from './pages/mapping/DataMappingWizard'
import { ProjectDetail } from './pages/projects/ProjectDetail'
import { ProjectList } from './pages/projects/ProjectList'
import { ReportBuilder } from './pages/reports/ReportBuilder'
import { CashFlowDetail } from './pages/results/CashFlowDetail'
import { PortfolioDashboard } from './pages/results/PortfolioDashboard'
import { ValuationResults } from './pages/results/ValuationResults'
import { RunMonitor } from './pages/runs/RunMonitor'
import { UploadCentre } from './pages/upload/UploadCentre'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/projects" replace /> },
      { path: 'projects', element: <ProjectList /> },
      {
        path: 'projects/:projectId',
        element: <ProjectLayout />,
        children: [
          { index: true, element: <ProjectDetail /> },
          { path: 'upload', element: <UploadCentre /> },
          { path: 'mapping/:uploadId', element: <DataMappingWizard /> },
          { path: 'extraction/:extractionId', element: <ExtractionReview /> },
          { path: 'assumptions', element: <AssumptionWorkbench /> },
          { path: 'runs', element: <RunMonitor /> },
          { path: 'runs/:runId/results', element: <ValuationResults /> },
          { path: 'runs/:runId/portfolio', element: <PortfolioDashboard /> },
          { path: 'runs/:runId/cashflow/:assetId', element: <CashFlowDetail /> },
          { path: 'reports', element: <ReportBuilder /> },
        ],
      },
      { path: 'admin/audit', element: <AuditLog /> },
    ],
  },
  {
    path: '/login',
    element: <AuthLayout />,
    children: [{ index: true, element: <Login /> }],
  },
])
