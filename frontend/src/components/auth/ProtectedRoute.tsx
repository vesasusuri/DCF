import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

function AuthLoading() {
  return (
    <div className="auth-loading">
      <div className="auth-loading-card card">
        <div className="page-eyebrow">DCF WORKBENCH</div>
        <p className="auth-loading-text">Sitzung wird geladen…</p>
      </div>
    </div>
  )
}

export function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) return <AuthLoading />
  if (!user) return <Navigate to="/login" replace />

  return <Outlet />
}

export function GuestRoute() {
  const { user, loading } = useAuth()

  if (loading) return <AuthLoading />

  if (user) {
    return <Navigate to={user.role === 'admin' ? '/admin' : '/projects'} replace />
  }

  return <Outlet />
}

export function UserRoute() {
  const { user, loading } = useAuth()

  if (loading) return null
  if (user?.role === 'admin') return <Navigate to="/admin" replace />

  return <Outlet />
}

export function AdminRoute() {
  const { user, loading } = useAuth()

  if (loading) return null
  if (!user || user.role !== 'admin') return <Navigate to="/projects" replace />

  return <Outlet />
}

export function RoleHomeRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'admin' ? '/admin' : '/projects'} replace />
}
