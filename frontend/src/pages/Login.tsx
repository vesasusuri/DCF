import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthShell } from '../components/auth/AuthShell'
import { formatAuthError, useAuth } from '../contexts/AuthContext'
import { getPostAuthPath } from '../lib/onboarding'

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
      navigate(getPostAuthPath(profile), { replace: true })
    } catch (err) {
      setError(formatAuthError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      eyebrow="ANMELDUNG"
      title="Willkommen zurück"
      subtitle="Melden Sie sich mit Ihrer E-Mail und dem temporären Passwort aus der Einladung an."
    >
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
    </AuthShell>
  )
}
