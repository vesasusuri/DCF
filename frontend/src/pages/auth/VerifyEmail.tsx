import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthShell } from '../../components/auth/AuthShell'
import { formatAuthError, useAuth } from '../../contexts/AuthContext'
import { getPostAuthPath } from '../../lib/onboarding'

export function VerifyEmail() {
  const { user, resendVerificationEmail, refreshUser } = useAuth()
  const navigate = useNavigate()
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [checking, setChecking] = useState(false)

  async function handleResend() {
    setSending(true)
    setError(null)
    setMessage(null)
    try {
      await resendVerificationEmail()
      setMessage('Bestätigungs-E-Mail wurde erneut gesendet.')
    } catch (err) {
      setError(formatAuthError(err))
    } finally {
      setSending(false)
    }
  }

  async function handleContinue() {
    setChecking(true)
    setError(null)
    try {
      const profile = await refreshUser()
      if (!profile) {
        navigate('/login', { replace: true })
        return
      }
      if (profile.onboardingStep === 'verify-email') {
        setError('E-Mail ist noch nicht bestätigt. Bitte prüfen Sie Ihr Postfach.')
        return
      }
      navigate(getPostAuthPath(profile), { replace: true })
    } catch (err) {
      setError(formatAuthError(err))
    } finally {
      setChecking(false)
    }
  }

  return (
    <AuthShell
      eyebrow="VERIFIZIERUNG"
      title="E-Mail bestätigen"
      subtitle="Wir haben Ihnen einen Bestätigungslink gesendet. Öffnen Sie die E-Mail und klicken Sie auf den Link."
    >
      <div className="auth-info-card card">
        <div className="auth-info-label">Ihre E-Mail</div>
        <div className="auth-info-value">{user?.email}</div>
      </div>

      {message && <div className="login-success">{message}</div>}
      {error && <div className="login-error">{error}</div>}

      <div className="auth-action-stack">
        <button
          type="button"
          className="btn btn-primary login-submit"
          onClick={() => void handleContinue()}
          disabled={checking}
        >
          {checking ? 'Prüfen…' : 'Ich habe bestätigt'}
        </button>

        <button
          type="button"
          className="btn btn-secondary login-submit"
          onClick={() => void handleResend()}
          disabled={sending}
        >
          {sending ? 'Senden…' : 'E-Mail erneut senden'}
        </button>
      </div>
    </AuthShell>
  )
}
