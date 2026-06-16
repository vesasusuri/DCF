import { useEffect, useState } from 'react'
import { AdminPageWrapper } from '../../components/layout/AdminLayout'
import { api, type AdminUser } from '../../lib/api'

function formatDate(value: string | null) {
  if (!value) return 'Noch nie'
  return new Date(value).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function AdminAudit() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.admin
      .listUsers()
      .then((data) =>
        setUsers(
          [...data].sort((a, b) => {
            const aTime = a.last_sign_in_at ? new Date(a.last_sign_in_at).getTime() : 0
            const bTime = b.last_sign_in_at ? new Date(b.last_sign_in_at).getTime() : 0
            return bTime - aTime
          }),
        ),
      )
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <AdminPageWrapper
      breadcrumbs={[
        { label: 'Admin Console' },
        { label: 'Audit', current: true },
      ]}
    >
      <div className="projects-page admin-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">A04 · AUDIT</div>
            <h1 className="page-title projects-title">Audit & Compliance</h1>
          </div>
        </div>

        {error && <div className="login-error admin-banner-error">{error}</div>}

        <div className="card admin-table-card">
          <div className="admin-table-header">
            <div>
              <div className="card-section-title">Letzte Anmeldungen</div>
              <div className="card-section-sub">Chronologische Übersicht aller Benutzeraktivitäten</div>
            </div>
          </div>

          <div className="admin-audit-list">
            {users.map((user) => (
              <div key={user.id} className="admin-audit-item">
                <div className="admin-audit-dot" />
                <div className="admin-audit-content">
                  <div className="admin-audit-title">
                    {user.full_name} <span>({user.email})</span>
                  </div>
                  <div className="admin-audit-meta">
                    Letzte Anmeldung: {formatDate(user.last_sign_in_at)} · Rolle:{' '}
                    {user.role === 'admin' ? 'Admin' : 'Benutzer'}
                  </div>
                </div>
                <span className={`badge ${user.last_sign_in_at ? 'badge-success' : 'badge-neutral'}`}>
                  {user.last_sign_in_at ? 'Aktiv' : 'Inaktiv'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AdminPageWrapper>
  )
}
