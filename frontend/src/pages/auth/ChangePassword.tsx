import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthShell } from '../../components/auth/AuthShell'
import { formatAuthError, useAuth } from '../../contexts/AuthContext'
import { getPostAuthPath } from '../../lib/onboarding'

export function ChangePassword() {
  const { changePassword } = useAuth()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (password.length < 8) {
      setError('Das Passwort muss mindestens 8 Zeichen lang sein.')
      return
    }

    if (password !== confirmPassword) {
      setError('Die Passwörter stimmen nicht überein.')
      return
    }

    setSubmitting(true)
    try {
      const profile = await changePassword(password)
      navigate(getPostAuthPath(profile), { replace: true })
    } catch (err) {
      setError(formatAuthError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      eyebrow="SICHERHEIT"
      title="Passwort ändern"
      subtitle="Bitte legen Sie ein neues Passwort fest, bevor Sie fortfahren."
    >
      <form className="login-form" onSubmit={handleSubmit}>
        <label className="form-field">
          <span className="form-label">Neues Passwort</span>
          <input
            className="form-input"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={8}
          />
        </label>

        <label className="form-field">
          <span className="form-label">Passwort bestätigen</span>
          <input
            className="form-input"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            required
            minLength={8}
          />
        </label>

        {error && <div className="login-error">{error}</div>}

        <button type="submit" className="btn btn-primary login-submit" disabled={submitting}>
          {submitting ? 'Speichern…' : 'Passwort speichern'}
        </button>
      </form>
    </AuthShell>
  )
}
