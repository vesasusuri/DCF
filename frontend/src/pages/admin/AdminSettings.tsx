import { useEffect, useState } from 'react'
import { AdminPageWrapper } from '../../components/layout/AdminLayout'
import { api } from '../../lib/api'

const settings = [
  { label: 'Umgebung', key: 'APP_ENV', value: 'development' },
  { label: 'API Prefix', key: 'API_PREFIX', value: '/api/v1' },
  { label: 'Dateispeicher', key: 'FILE_STORAGE_PROVIDER', value: 'supabase' },
  { label: 'CORS Origins', key: 'CORS_ORIGINS', value: 'localhost:5173, localhost:8080' },
]

export function AdminSettings() {
  const [health, setHealth] = useState<{ status: string; environment: string } | null>(null)

  useEffect(() => {
    api.getHealth().then(setHealth).catch(() => setHealth(null))
  }, [])

  return (
    <AdminPageWrapper
      breadcrumbs={[
        { label: 'Admin Console' },
        { label: 'Einstellungen', current: true },
      ]}
    >
      <div className="projects-page admin-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">A03 · EINSTELLUNGEN</div>
            <h1 className="page-title projects-title">Systemeinstellungen</h1>
          </div>
        </div>

        <div className="admin-settings-grid">
          <div className="card admin-settings-card">
            <div className="card-section-title">API-Status</div>
            <div className="admin-settings-rows">
              <div className="admin-settings-row">
                <span>Status</span>
                <span className={`badge ${health?.status === 'ok' ? 'badge-success' : 'badge-neutral'}`}>
                  {health?.status ?? 'unbekannt'}
                </span>
              </div>
              <div className="admin-settings-row">
                <span>Umgebung</span>
                <strong>{health?.environment ?? '—'}</strong>
              </div>
            </div>
          </div>

          <div className="card admin-settings-card">
            <div className="card-section-title">Konfiguration</div>
            <div className="admin-settings-rows">
              {settings.map((item) => (
                <div key={item.key} className="admin-settings-row">
                  <span>{item.label}</span>
                  <code className="admin-code">{item.value}</code>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AdminPageWrapper>
  )
}
