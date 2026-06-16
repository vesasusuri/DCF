import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDefaultRouteForRole, formatAuthError, useAuth } from '../contexts/AuthContext'

export function Login() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      const profile = await signIn(email.trim(), password)
      navigate(getDefaultRouteForRole(profile.role), { replace: true })
    } catch (err) {
      setError(formatAuthError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-shell">
      <div className="app-brand-gradient" aria-hidden="true" />

      <div className="login-page">
        <div className="login-card card">
          <div className="login-card-gradient" aria-hidden="true" />

          <div className="login-brand">
            <div className="login-logo-icon">C</div>
            <div>
              <div className="login-logo-title">DCF Workbench</div>
              <div className="login-logo-sub">BOREK × COLLIERS</div>
            </div>
          </div>

          <div className="login-header">
            <div className="page-eyebrow login-eyebrow">ANMELDUNG</div>
            <h1 className="page-title login-title">Willkommen zurück</h1>
            <p className="login-subtitle">
              Melden Sie sich an, um auf Ihre Bewertungsprojekte zuzugreifen.
            </p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="form-field">
              <span className="form-label">E-Mail</span>
              <input
                className="form-input"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="name@unternehmen.de"
                required
              />
            </label>

            <label className="form-field">
              <span className="form-label">Passwort</span>
              <input
                className="form-input"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                required
              />
            </label>

            {error && <div className="login-error">{error}</div>}

            <button type="submit" className="btn btn-primary login-submit" disabled={submitting}>
              {submitting ? 'Anmeldung…' : 'Anmelden'}
            </button>
          </form>

          <div className="login-hint card">
            <div className="login-hint-title">Demo-Zugänge</div>
            <div className="login-hint-row">
              <span className="badge badge-neutral">User</span>
              <span>user@example.com · User1234!</span>
            </div>
            <div className="login-hint-row">
              <span className="badge badge-warning">Admin</span>
              <span>admin@example.com · Admin1234!</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
