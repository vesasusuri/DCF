import { useState } from 'react'
import { Plus } from 'lucide-react'
import { PageWrapper } from '../components/layout/MainLayout'

type ProjectStatus = 'Prüfung' | 'Fertig' | 'Entwurf'

type Project = {
  id: string
  title: string
  subtitle: string
  status: ProjectStatus
  statusDetail: string
  team: string
}

const projects: Project[] = [
  {
    id: '1',
    title: 'LI Portfolio NRW',
    subtitle: 'Colliers Germany · 47 Assets',
    status: 'Prüfung',
    statusDetail: 'Lauf #14 · vor 2 Std.',
    team: 'Team Rhein-Ruhr',
  },
  {
    id: '2',
    title: 'Light Industrial Süd',
    subtitle: 'Aurelis Real Estate · 31 Assets',
    status: 'Fertig',
    statusDetail: 'Lauf #08 · gestern',
    team: 'Team München',
  },
  {
    id: '3',
    title: 'Logistics Core DE',
    subtitle: 'Garbe Industrial · 62 Assets',
    status: 'Fertig',
    statusDetail: 'Lauf #21 · vor 3 Tagen',
    team: 'Team Nord',
  },
  {
    id: '4',
    title: 'Urban Logistics Mix',
    subtitle: 'Deka Immobilien · 24 Assets',
    status: 'Entwurf',
    statusDetail: 'Entwurf · kein Lauf',
    team: 'Team Frankfurt',
  },
  {
    id: '5',
    title: 'Unternehmensimmobilien',
    subtitle: 'BEOS AG · 53 Assets',
    status: 'Prüfung',
    statusDetail: 'Lauf #05 · letzte Woche',
    team: 'Team Berlin',
  },
]

const statusBadgeClass: Record<ProjectStatus, string> = {
  Prüfung: 'badge-warning',
  Fertig: 'badge-success',
  Entwurf: 'badge-neutral',
}

const tabs = ['Alle', 'Aktiv', 'Archiviert']

export function ProjectsOverview() {
  const [activeTab, setActiveTab] = useState('Alle')

  return (
    <PageWrapper
      breadcrumbs={[
        { label: 'Colliers Germany' },
        { label: 'Alle Projekte', current: true },
      ]}
    >
      <div className="page-eyebrow">S01 · PROJEKTE</div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Alle Bewertungsprojekte</h1>
          <div className="tabs" style={{ marginTop: 16 }}>
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`tab${activeTab === tab ? ' active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary">Importieren</button>
          <button className="btn btn-primary">+ Neues Projekt</button>
        </div>
      </div>

      <div className="kpi-bar">
        <div className="kpi-item">
          <div className="kpi-label">Offene Projekte</div>
          <div className="kpi-value">12</div>
          <div className="kpi-sub">über 4 Teams</div>
        </div>
        <div className="kpi-item">
          <div className="kpi-label">Assets im Scope</div>
          <div className="kpi-value">318</div>
          <div className="kpi-sub">1.940 Leases</div>
        </div>
        <div className="kpi-item">
          <div className="kpi-label">Wartet auf Review</div>
          <div className="kpi-value">5</div>
          <div className="kpi-sub">
            Datenqualitäts-Flags <span className="kpi-action">Aktion</span>
          </div>
        </div>
        <div className="kpi-item">
          <div className="kpi-label">Berichte / Monat</div>
          <div className="kpi-value">9</div>
          <div className="kpi-sub">PDF / Excel</div>
        </div>
      </div>

      <div className="project-grid">
        {projects.map((project) => (
          <div key={project.id} className="project-card">
            <div className="project-card-header">
              <div>
                <div className="project-card-title">{project.title}</div>
                <div className="project-card-sub">{project.subtitle}</div>
              </div>
              <span className={`badge ${statusBadgeClass[project.status]}`}>
                {project.status}
              </span>
            </div>
            <div className="project-card-status">{project.statusDetail}</div>
            <div className="project-card-footer">
              <span className="project-card-team">{project.team}</span>
              <div className="project-card-actions">
                <button className="btn-link-primary">Öffnen</button>
                <button className="btn-link">DCF starten →</button>
              </div>
            </div>
          </div>
        ))}

        <div className="project-card project-card-new">
          <div className="project-card-new-icon">
            <Plus size={22} />
          </div>
          <div className="project-card-new-title">Bewertungsprojekt anlegen</div>
          <div className="project-card-new-sub">
            Client · Währung · Bewertungsstichtag · Reporting-Sprache
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
