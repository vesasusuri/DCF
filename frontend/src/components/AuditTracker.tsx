import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { recordPageView } from '../lib/audit'

export function AuditTracker() {
  const { pathname } = useLocation()
  const { user, loading } = useAuth()

  useEffect(() => {
    if (loading || !user || pathname === '/login') return
    if (pathname.startsWith('/auth/')) return
    if (user.onboardingStep !== 'complete') return
    recordPageView(pathname)
  }, [loading, pathname, user])

  return null
}
