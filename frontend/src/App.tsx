import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import {
  AdminRoute,
  GuestRoute,
  ProtectedRoute,
  RoleHomeRedirect,
  UserRoute,
} from './components/auth/ProtectedRoute'
import { AdminLayout } from './components/layout/AdminLayout'
import { MainLayout, PageWrapper } from './components/layout/MainLayout'
import { AdminAudit } from './pages/admin/AdminAudit'
import { AdminOverview } from './pages/admin/AdminOverview'
import { AdminSecurity } from './pages/admin/AdminSecurity'
import { AdminSettings } from './pages/admin/AdminSettings'
import { AdminUsers } from './pages/admin/AdminUsers'
import { ProjectsOverview } from './pages/ProjectsOverview'
import { UploadHub } from './pages/UploadHub'
import { DataMapping } from './pages/DataMapping'
import { ExtractionReview } from './pages/ExtractionReview'
import { Login } from './pages/Login'

function PlaceholderPage({ title, code }: { title: string; code: string }) {
  return (
    <PageWrapper breadcrumbs={[{ label: title, current: true }]}>
      <div className="page-eyebrow">{code}</div>
      <h1 className="page-title">{title}</h1>
      <p style={{ color: 'var(--color-text-muted)', marginTop: 16 }}>
        Dieser Bereich wird in Kürze verfügbar sein.
      </p>
    </PageWrapper>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<GuestRoute />}>
          <Route path="/login" element={<Login />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route index element={<RoleHomeRedirect />} />

          <Route element={<UserRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/projects" element={<ProjectsOverview />} />
              <Route path="/upload" element={<UploadHub />} />
              <Route path="/upload/mapping" element={<DataMapping />} />
              <Route path="/data-review/extraction" element={<ExtractionReview />} />
              <Route path="/assumptions" element={<PlaceholderPage title="Annahmen" code="S05" />} />
              <Route path="/runs" element={<PlaceholderPage title="Bewertungsläufe" code="S06" />} />
              <Route path="/results" element={<PlaceholderPage title="Ergebnisse" code="S07" />} />
              <Route path="/dashboards" element={<PlaceholderPage title="Dashboards" code="S08" />} />
              <Route path="/reports" element={<PlaceholderPage title="Berichte" code="S18" />} />
            </Route>
          </Route>

          <Route element={<AdminRoute />}>
            <Route element={<AdminLayout />}>
              <Route path="/admin" element={<AdminOverview />} />
              <Route path="/admin/users" element={<AdminUsers />} />
              <Route path="/admin/settings" element={<AdminSettings />} />
              <Route path="/admin/audit" element={<AdminAudit />} />
              <Route path="/admin/security" element={<AdminSecurity />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
