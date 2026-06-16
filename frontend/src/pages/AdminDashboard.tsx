import { Shield, Users, Settings, Activity } from 'lucide-react'
import { PageWrapper } from '../components/layout/MainLayout'
import { useAuth } from '../contexts/AuthContext'

const adminCards = [
  {
    title: 'Benutzerverwaltung',
    subtitle: 'Rollen, Teams und Zugriffsrechte',
    icon: Users,
    badge: '12 Benutzer',
  },
  {
    title: 'Systemeinstellungen',
    subtitle: 'Mandanten, Integrationen, API-Schlüssel',
    icon: Settings,
    badge: 'Konfiguration',
  },
  {
    title: 'Audit & Compliance',
    subtitle: 'Protokolle, Exporte, Datenhaltung',
    icon: Activity,
    badge: 'Letzte 24h',
  },
  {
    title: 'Sicherheit',
    subtitle: 'SSO, 2FA, Sitzungsrichtlinien',
    icon: Shield,
    badge: 'Aktiv',
  },
]

export function AdminDashboard() {
  const { user } = useAuth()

  return (
    <PageWrapper
      breadcrumbs={[
        { label: 'Colliers Germany' },
        { label: 'Admin', current: true },
      ]}
    >
      <div className="projects-page admin-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">S11 · ADMIN</div>
            <h1 className="page-title projects-title">Systemverwaltung</h1>
          </div>

          <div className="page-actions">
            <button type="button" className="btn btn-secondary">
              Export
            </button>
            <button type="button" className="btn btn-primary">
              + Benutzer einladen
            </button>
          </div>
        </div>

        <div className="kpi-bar">
          <div className="kpi-item">
            <div className="kpi-label">Angemeldet als</div>
            <div className="kpi-value admin-kpi-value">{user?.fullName ?? 'Admin'}</div>
            <div className="kpi-sub">{user?.email}</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Rolle</div>
            <div className="kpi-value admin-kpi-value">Admin</div>
            <div className="kpi-sub">Vollzugriff auf Systembereiche</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Aktive Benutzer</div>
            <div className="kpi-value">12</div>
            <div className="kpi-sub">über 4 Teams</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Systemstatus</div>
            <div className="kpi-value">OK</div>
            <div className="kpi-sub-row">
              <span className="kpi-sub">API · DB · Redis</span>
              <span className="kpi-action" style={{ color: 'var(--color-success)' }}>
                Online
              </span>
            </div>
          </div>
        </div>

        <div className="admin-grid">
          {adminCards.map((card) => {
            const Icon = card.icon
            return (
              <div key={card.title} className="project-card admin-card">
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
                  <span className="badge badge-neutral">{card.badge}</span>
                </div>
                <div className="project-card-footer">
                  <span className="project-card-team">Nur für Administratoren</span>
                  <button type="button" className="btn-link-primary">
                    Öffnen
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </PageWrapper>
  )
}
