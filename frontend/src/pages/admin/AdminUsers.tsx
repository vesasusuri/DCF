import { useEffect, useState, type FormEvent } from 'react'
import { AdminPageWrapper } from '../../components/layout/AdminLayout'
import { api, type AdminUser, type CreateAdminUserPayload } from '../../lib/api'

function formatDate(value: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const emptyInvite: CreateAdminUserPayload = {
  email: '',
  password: '',
  full_name: '',
  role: 'user',
}

export function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [inviteOpen, setInviteOpen] = useState(false)
  const [invite, setInvite] = useState(emptyInvite)
  const [saving, setSaving] = useState(false)

  async function loadUsers() {
    setLoading(true)
    setError(null)
    try {
      const data = await api.admin.listUsers()
      setUsers(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Benutzer konnten nicht geladen werden.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadUsers()
  }, [])

  async function handleInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await api.admin.createUser(invite)
      setInvite(emptyInvite)
      setInviteOpen(false)
      await loadUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Benutzer konnte nicht erstellt werden.')
    } finally {
      setSaving(false)
    }
  }

  async function toggleRole(user: AdminUser) {
    const nextRole = user.role === 'admin' ? 'user' : 'admin'
    setError(null)
    try {
      await api.admin.updateUser(user.id, { role: nextRole })
      await loadUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rolle konnte nicht geändert werden.')
    }
  }

  return (
    <AdminPageWrapper
      breadcrumbs={[
        { label: 'Admin Console' },
        { label: 'Benutzer', current: true },
      ]}
    >
      <div className="projects-page admin-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">A02 · BENUTZER</div>
            <h1 className="page-title projects-title">Benutzerverwaltung</h1>
          </div>

          <div className="page-actions">
            <button type="button" className="btn btn-secondary" onClick={() => void loadUsers()}>
              Aktualisieren
            </button>
            <button type="button" className="btn btn-primary" onClick={() => setInviteOpen(true)}>
              + Benutzer einladen
            </button>
          </div>
        </div>

        {error && <div className="login-error admin-banner-error">{error}</div>}

        <div className="card admin-table-card">
          <div className="admin-table-header">
            <div>
              <div className="card-section-title">Alle Benutzer</div>
              <div className="card-section-sub">{users.length} Konten im System</div>
            </div>
          </div>

          {loading ? (
            <div className="admin-empty-state">Benutzer werden geladen…</div>
          ) : (
            <div className="admin-table-wrap">
              <table className="data-table admin-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>E-Mail</th>
                    <th>Rolle</th>
                    <th>Erstellt</th>
                    <th>Letzte Anmeldung</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.full_name}</td>
                      <td>{user.email}</td>
                      <td>
                        <span className={`badge ${user.role === 'admin' ? 'badge-warning' : 'badge-neutral'}`}>
                          {user.role === 'admin' ? 'Admin' : 'Benutzer'}
                        </span>
                      </td>
                      <td>{formatDate(user.created_at)}</td>
                      <td>{formatDate(user.last_sign_in_at)}</td>
                      <td className="admin-table-actions">
                        <button
                          type="button"
                          className="btn-link-primary"
                          onClick={() => void toggleRole(user)}
                        >
                          {user.role === 'admin' ? 'Zu Benutzer' : 'Zu Admin'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {inviteOpen && (
          <div className="admin-modal-backdrop" onClick={() => setInviteOpen(false)}>
            <div className="card admin-modal" onClick={(event) => event.stopPropagation()}>
              <div className="page-eyebrow login-eyebrow">NEUER BENUTZER</div>
              <h2 className="admin-modal-title">Benutzer einladen</h2>

              <form className="login-form" onSubmit={handleInvite}>
                <label className="form-field">
                  <span className="form-label">Vollständiger Name</span>
                  <input
                    className="form-input"
                    value={invite.full_name}
                    onChange={(event) => setInvite({ ...invite, full_name: event.target.value })}
                    required
                  />
                </label>

                <label className="form-field">
                  <span className="form-label">E-Mail</span>
                  <input
                    className="form-input"
                    type="email"
                    value={invite.email}
                    onChange={(event) => setInvite({ ...invite, email: event.target.value })}
                    required
                  />
                </label>

                <label className="form-field">
                  <span className="form-label">Passwort</span>
                  <input
                    className="form-input"
                    type="password"
                    value={invite.password}
                    onChange={(event) => setInvite({ ...invite, password: event.target.value })}
                    minLength={8}
                    required
                  />
                </label>

                <label className="form-field">
                  <span className="form-label">Rolle</span>
                  <select
                    className="form-input"
                    value={invite.role}
                    onChange={(event) =>
                      setInvite({ ...invite, role: event.target.value as 'user' | 'admin' })
                    }
                  >
                    <option value="user">Benutzer</option>
                    <option value="admin">Admin</option>
                  </select>
                </label>

                <div className="admin-modal-actions">
                  <button type="button" className="btn btn-secondary" onClick={() => setInviteOpen(false)}>
                    Abbrechen
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? 'Speichern…' : 'Benutzer anlegen'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AdminPageWrapper>
  )
}
