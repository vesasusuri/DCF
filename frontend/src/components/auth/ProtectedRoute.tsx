import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="auth-loading">
        <div className="auth-loading-card card">
          <div className="page-eyebrow">DCF WORKBENCH</div>
          <p className="auth-loading-text">Sitzung wird geladen…</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export function GuestRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="auth-loading">
        <div className="auth-loading-card card">
          <div className="page-eyebrow">DCF WORKBENCH</div>
          <p className="auth-loading-text">Sitzung wird geladen…</p>
        </div>
      </div>
    )
  }

  if (user) {
    return <Navigate to={user.role === 'admin' ? '/admin' : '/projects'} replace />
  }

  return <Outlet />
}

export function AdminRoute() {
  const { user, loading } = useAuth()

  if (loading) return null

  if (!user || user.role !== 'admin') {
    return <Navigate to="/projects" replace />
  }

  return <Outlet />
}
