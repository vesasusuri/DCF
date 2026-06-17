import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Users, Settings, Activity, Shield } from 'lucide-react'
import { AdminPageWrapper } from '../../components/layout/AdminLayout'
import { api, type AdminStats, type AuditLog } from '../../lib/api'
import { actionLabel, formatAuditDetails } from '../../lib/auditDisplay'
import { useAuth } from '../../contexts/AuthContext'

function formatLogTime(value: string) {
  return new Date(value).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const quickLinks = [
  { title: 'Benutzerverwaltung', subtitle: 'Konten anlegen und Rollen zuweisen', icon: Users, path: '/admin/users', code: 'A02' },
  { title: 'Systemeinstellungen', subtitle: 'Umgebung und Integrationen', icon: Settings, path: '/admin/settings', code: 'A03' },
  { title: 'Audit & Compliance', subtitle: 'Anmeldungen und Aktivitäten', icon: Activity, path: '/admin/audit', code: 'A04' },
  { title: 'Sicherheit', subtitle: 'Richtlinien und Zugriffskontrolle', icon: Shield, path: '/admin/security', code: 'A05' },
]

export function AdminOverview() {
  const { user } = useAuth()
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [recentLogs, setRecentLogs] = useState<AuditLog[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.admin
      .getStats()
      .then(setStats)
      .catch((err: Error) => setError(err.message))

    api.admin
      .listLogs(1, 5)
      .then((data) => setRecentLogs(data.items))
      .catch(() => undefined)
  }, [])

  return (
    <AdminPageWrapper
      breadcrumbs={[
        { label: 'Admin Console' },
        { label: 'Übersicht', current: true },
      ]}
    >
      <div className="projects-page admin-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">A01 · ÜBERSICHT</div>
            <h1 className="page-title projects-title">Systemverwaltung</h1>
          </div>

          <div className="page-actions">
            <Link to="/admin/users" className="btn btn-secondary">
              Benutzer
            </Link>
            <Link to="/admin/users" className="btn btn-primary">
              + Benutzer einladen
            </Link>
          </div>
        </div>

        {error && <div className="login-error admin-banner-error">{error}</div>}

        <div className="kpi-bar">
          <div className="kpi-item">
            <div className="kpi-label">Angemeldet als</div>
            <div className="kpi-value admin-kpi-value">{user?.fullName ?? 'Admin'}</div>
            <div className="kpi-sub">{user?.email}</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Benutzer gesamt</div>
            <div className="kpi-value">{stats?.users_total ?? '—'}</div>
            <div className="kpi-sub">{stats?.admins_total ?? 0} Administratoren</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Aktiv (24h)</div>
            <div className="kpi-value">{stats?.users_active_24h ?? '—'}</div>
            <div className="kpi-sub">Letzte Anmeldungen</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Systemstatus</div>
            <div className="kpi-value">{stats?.api_status === 'ok' ? 'OK' : '—'}</div>
            <div className="kpi-sub-row">
              <span className="kpi-sub">API · {stats?.environment ?? '—'}</span>
              <span className="kpi-action" style={{ color: 'var(--color-success)' }}>
                Online
              </span>
            </div>
          </div>
        </div>

        <div className="admin-grid">
          {quickLinks.map((card) => {
            const Icon = card.icon
            return (
              <Link key={card.path} to={card.path} className="project-card admin-card admin-card-link">
                <div className="project-card-header">
                  <div className="admin-card-title-row">
                    <div className="admin-card-icon">
                      <Icon size={18} />
                    </div>
                    <div>
                      <div className="project-card-title">{card.title}</div>
                      <div className="project-card-sub">{card.subtitle}</div>
                    </div>
                  </div>
                  <span className="badge badge-neutral">{card.code}</span>
                </div>
                <div className="project-card-footer">
                  <span className="project-card-team">Admin-Bereich</span>
                  <span className="btn-link-primary">Öffnen →</span>
                </div>
              </Link>
            )
          })}
        </div>

        <div className="card admin-table-card admin-recent-logs">
          <div className="admin-recent-logs-header">
            <div>
              <div className="card-section-title">Letzte Aktivitäten</div>
              <div className="card-section-sub">Die fünf neuesten Protokolleinträge</div>
            </div>
            <Link to="/admin/audit" className="btn-link-primary">
              Alle anzeigen →
            </Link>
          </div>

          {recentLogs.length === 0 ? (
            <div className="admin-empty-state">Noch keine Aktivitäten protokolliert.</div>
          ) : (
            <div className="admin-audit-list">
              {recentLogs.map((log) => (
                <div key={log.id} className="admin-audit-item">
                  <div className="admin-audit-dot" />
                  <div className="admin-audit-content">
                    <div className="admin-audit-title">
                      {actionLabel(log.action)}{' '}
                      <span>({log.actor_name ?? log.actor_email ?? 'System'})</span>
                    </div>
                    <div className="admin-audit-meta">
                      {formatLogTime(log.created_at)} · {formatAuditDetails(log)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AdminPageWrapper>
  )
}
