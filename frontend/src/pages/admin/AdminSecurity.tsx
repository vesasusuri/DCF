import { AdminPageWrapper } from '../../components/layout/AdminLayout'

const policies = [
  {
    title: 'Rollenbasierte Zugriffskontrolle',
    detail: 'Admins sehen ausschließlich die Admin Console. Benutzer haben keinen Zugriff auf Admin-Routen.',
    status: 'Aktiv',
  },
  {
    title: 'Passwort-Mindestlänge',
    detail: 'Neue Konten benötigen mindestens 8 Zeichen.',
    status: 'Aktiv',
  },
  {
    title: 'E-Mail-Bestätigung',
    detail: 'Von Administratoren angelegte Konten werden automatisch bestätigt.',
    status: 'Aktiv',
  },
  {
    title: 'JWT-Sitzungen',
    detail: 'Supabase Auth verwaltet Sitzungen und Token-Erneuerung.',
    status: 'Aktiv',
  },
]

export function AdminSecurity() {
  return (
    <AdminPageWrapper
      breadcrumbs={[
        { label: 'Admin Console' },
        { label: 'Sicherheit', current: true },
      ]}
    >
      <div className="projects-page admin-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">A05 · SICHERHEIT</div>
            <h1 className="page-title projects-title">Sicherheit</h1>
          </div>
        </div>

        <div className="admin-grid">
          {policies.map((policy) => (
            <div key={policy.title} className="project-card admin-card">
              <div className="project-card-header">
                <div>
                  <div className="project-card-title">{policy.title}</div>
                  <div className="project-card-sub">{policy.detail}</div>
                </div>
                <span className="badge badge-success">{policy.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AdminPageWrapper>
  )
}
