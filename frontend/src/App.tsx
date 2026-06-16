import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AdminRoute, GuestRoute, ProtectedRoute } from './components/auth/ProtectedRoute'
import { MainLayout, PageWrapper } from './components/layout/MainLayout'
import { AdminDashboard } from './pages/AdminDashboard'
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
          <Route element={<MainLayout />}>
            <Route index element={<Navigate to="/projects" replace />} />
            <Route path="/projects" element={<ProjectsOverview />} />
            <Route path="/upload" element={<UploadHub />} />
            <Route path="/upload/mapping" element={<DataMapping />} />
            <Route path="/data-review/extraction" element={<ExtractionReview />} />
            <Route path="/assumptions" element={<PlaceholderPage title="Annahmen" code="S05" />} />
            <Route path="/runs" element={<PlaceholderPage title="Bewertungsläufe" code="S06" />} />
            <Route path="/results" element={<PlaceholderPage title="Ergebnisse" code="S07" />} />
            <Route path="/dashboards" element={<PlaceholderPage title="Dashboards" code="S08" />} />
            <Route path="/reports" element={<PlaceholderPage title="Berichte" code="S18" />} />

            <Route element={<AdminRoute />}>
              <Route path="/admin" element={<AdminDashboard />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
