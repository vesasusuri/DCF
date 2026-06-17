import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthShell } from '../../components/auth/AuthShell'
import { useAuth } from '../../contexts/AuthContext'
import { getPostAuthPath } from '../../lib/onboarding'
import { supabase } from '../../lib/supabase'

export function AuthCallback() {
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function handleCallback() {
      if (!supabase) {
        navigate('/login', { replace: true })
        return
      }

      await new Promise((resolve) => setTimeout(resolve, 300))

      const { data: sessionData } = await supabase.auth.getSession()
      const sessionUser = sessionData.session?.user
      if (
        sessionUser?.user_metadata?.invited === true &&
        sessionUser.user_metadata.email_verified !== true
      ) {
        await supabase.auth.updateUser({ data: { email_verified: true } })
      }

      const profile = await refreshUser()
      if (!profile) {
        setError('Bestätigung fehlgeschlagen. Bitte melden Sie sich erneut an.')
        return
      }

      navigate(getPostAuthPath(profile), { replace: true })
    }

    void handleCallback()
  }, [navigate, refreshUser])

  if (error) {
    return (
      <AuthShell eyebrow="VERIFIZIERUNG" title="Bestätigung fehlgeschlagen" subtitle={error}>
        <button type="button" className="btn btn-primary login-submit" onClick={() => navigate('/login')}>
          Zur Anmeldung
        </button>
      </AuthShell>
    )
  }

  return (
    <AuthShell
      eyebrow="VERIFIZIERUNG"
      title="E-Mail wird bestätigt…"
      subtitle="Bitte einen Moment warten."
    >
      <div className="auth-info-card card">
        <p className="auth-loading-text">Sitzung wird aktualisiert…</p>
      </div>
    </AuthShell>
  )
}
