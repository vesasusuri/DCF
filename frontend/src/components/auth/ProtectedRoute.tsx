import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { getPostAuthPath } from '../../lib/onboarding'

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
    return <Navigate to={getPostAuthPath(user)} replace />
  }

  return <Outlet />
}

export function OnboardingRoute() {
  const { user, loading } = useAuth()

  if (loading) return <AuthLoading />
  if (!user) return <Navigate to="/login" replace />

  if (user.onboardingStep === 'complete') {
    return <Navigate to={getPostAuthPath(user)} replace />
  }

  return <Outlet />
}

export function OnboardingGate() {
  const { user, loading } = useAuth()

  if (loading) return null

  if (user?.onboardingStep === 'change-password') {
    return <Navigate to="/auth/change-password" replace />
  }

  if (user?.onboardingStep === 'verify-email') {
    return <Navigate to="/auth/verify-email" replace />
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
  return <Navigate to={getPostAuthPath(user)} replace />
}
