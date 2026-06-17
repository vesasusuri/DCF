import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Plus } from 'lucide-react'
import { PageWrapper } from '../components/layout/MainLayout'
import { useAuth } from '../contexts/AuthContext'
import { useCreateProject } from '../hooks/useCreateProject'
import { useDashboardStats } from '../hooks/useDashboardStats'
import { useProjects } from '../hooks/useProjects'
import { ApiError } from '../lib/api'
import {
  countUniqueTeams,
  formatProjectStatusDetail,
  formatProjectSubtitle,
  getProjectStatusBadgeClass,
  getProjectStatusLabel,
} from '../lib/projectFormatters'
import type { CreateProjectPayload, ProjectSummary } from '../types/project'

const tabs = ['Alle', 'Aktiv', 'Archiviert']

const emptyCreateForm: CreateProjectPayload = {
  client: '',
  projectName: '',
  currency: 'EUR',
  valuationDate: '',
  reportingLanguage: 'de',
}

function tabToStatus(tab: string): string | undefined {
  if (tab === 'Aktiv') return 'active'
  if (tab === 'Archiviert') return 'archived'
  return undefined
}

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    if (error.status === 403) {
      return 'Keine Berechtigung für das Portfolio-Manager-Dashboard.'
    }
    return error.message
  }
  if (error instanceof Error) return error.message
  return fallback
}

export function ProjectsOverview() {
  const { user } = useAuth()
  const isPortfolioManager = user?.role === 'portfolio_manager'

  const [activeTab, setActiveTab] = useState('Alle')
  const [searchInput, setSearchInput] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [createForm, setCreateForm] = useState(emptyCreateForm)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedSearch(searchInput.trim()), 300)
    return () => window.clearTimeout(timeout)
  }, [searchInput])

  const listParams = useMemo(
    () => ({
      page: 1,
      limit: 20,
      status: tabToStatus(activeTab),
      search: debouncedSearch || undefined,
    }),
    [activeTab, debouncedSearch],
  )

  const statsQuery = useDashboardStats(isPortfolioManager)
  const projectsQuery = useProjects(listParams, isPortfolioManager)
  const createProject = useCreateProject()

  const projects = projectsQuery.data?.items ?? []
  const teamCount = countUniqueTeams(projects)

  const loadError =
    statsQuery.error || projectsQuery.error
      ? getErrorMessage(
          statsQuery.error ?? projectsQuery.error,
          'Dashboard-Daten konnten nicht geladen werden.',
        )
      : null

  const permissionError =
    !isPortfolioManager && user
      ? 'Nur Portfolio Manager können auf die Bewertungsprojekte zugreifen.'
      : null

  function openCreateModal() {
    setFormError(null)
    setCreateForm(emptyCreateForm)
    setCreateOpen(true)
  }

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    try {
      await createProject.mutateAsync(createForm)
      setCreateOpen(false)
      setCreateForm(emptyCreateForm)
    } catch (error) {
      setFormError(getErrorMessage(error, 'Projekt konnte nicht erstellt werden.'))
    }
  }

  return (
    <PageWrapper
      breadcrumbs={[
        { label: 'Colliers Germany' },
        { label: 'Alle Projekte', current: true },
      ]}
      searchValue={searchInput}
      onSearchChange={setSearchInput}
    >
      <div className="projects-page">
        <div className="projects-header-bar">
          <div className="projects-header-title">
            <div className="page-eyebrow projects-eyebrow">S01 · PROJEKTE</div>
            <h1 className="page-title projects-title">Alle Bewertungsprojekte</h1>
          </div>

          <div className="projects-tabs">
            {tabs.map((tab) => (
              <button
                key={tab}
                type="button"
                className={`projects-tab${activeTab === tab ? ' active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="page-actions">
            <button type="button" className="btn btn-secondary">
              Importieren
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={openCreateModal}
              disabled={!isPortfolioManager}
            >
              + Neues Projekt
            </button>
          </div>
        </div>

        {(permissionError || loadError) && (
          <div className="login-error admin-banner-error">{permissionError ?? loadError}</div>
        )}

        <div className="kpi-bar">
          <div className="kpi-item">
            <div className="kpi-label">Offene Projekte</div>
            <div className="kpi-value">
              {statsQuery.isLoading ? '—' : (statsQuery.data?.openProjects ?? '—')}
            </div>
            <div className="kpi-sub">
              {teamCount > 0 ? `über ${teamCount} Teams` : '—'}
            </div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Assets im Scope</div>
            <div className="kpi-value">
              {statsQuery.isLoading ? '—' : (statsQuery.data?.assetsWithinScope ?? '—')}
            </div>
            <div className="kpi-sub">Assets gesamt</div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Wartet auf Review</div>
            <div className="kpi-value">
              {statsQuery.isLoading ? '—' : (statsQuery.data?.awaitingReview ?? '—')}
            </div>
            <div className="kpi-sub-row">
              <span className="kpi-sub">Datenqualitäts-Flags</span>
              <span className="kpi-action">Aktion</span>
            </div>
          </div>
          <div className="kpi-item">
            <div className="kpi-label">Berichte / Monat</div>
            <div className="kpi-value">
              {statsQuery.isLoading ? '—' : (statsQuery.data?.reportsPerMonth ?? '—')}
            </div>
            <div className="kpi-sub">PDF / Excel</div>
          </div>
        </div>

        {projectsQuery.isLoading && isPortfolioManager ? (
          <div className="admin-empty-state">Projekte werden geladen…</div>
        ) : (
          <>
            {!projectsQuery.isLoading && isPortfolioManager && projects.length === 0 && (
              <div className="admin-empty-state">Keine Projekte für die aktuelle Auswahl gefunden.</div>
            )}

            <div className="project-grid">
            {projects.map((project: ProjectSummary) => (
              <div key={project.id} className="project-card">
                <div className="project-card-header">
                  <div>
                    <div className="project-card-title">{project.projectName}</div>
                    <div className="project-card-sub">{formatProjectSubtitle(project)}</div>
                  </div>
                  <span className={`badge ${getProjectStatusBadgeClass(project.status)}`}>
                    {getProjectStatusLabel(project.status)}
                  </span>
                </div>
                <div className="project-card-status">
                  {formatProjectStatusDetail(project)}
                </div>
                <div className="project-card-footer">
                  <span className="project-card-team">{project.assignedTeam ?? '—'}</span>
                  <div className="project-card-actions">
                    <button type="button" className="btn-link-primary">
                      Öffnen
                    </button>
                    <button type="button" className="btn-link">
                      DCF starten →
                    </button>
                  </div>
                </div>
              </div>
            ))}

            <div
              role="button"
              tabIndex={isPortfolioManager ? 0 : -1}
              className="project-card project-card-new"
              onClick={isPortfolioManager ? openCreateModal : undefined}
              onKeyDown={(event) => {
                if (!isPortfolioManager) return
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault()
                  openCreateModal()
                }
              }}
            >
              <div className="project-card-new-icon">
                <Plus size={22} />
              </div>
              <div className="project-card-new-title">Bewertungsprojekt anlegen</div>
              <div className="project-card-new-sub">
                Client · Währung · Bewertungsstichtag · Reporting-Sprache
              </div>
            </div>
            </div>
          </>
        )}

        {createOpen && (
          <div className="admin-modal-backdrop" onClick={() => setCreateOpen(false)}>
            <div className="card admin-modal" onClick={(event) => event.stopPropagation()}>
              <div className="page-eyebrow login-eyebrow">NEUES PROJEKT</div>
              <h2 className="admin-modal-title">Bewertungsprojekt anlegen</h2>

              {formError && <div className="login-error">{formError}</div>}

              <form className="login-form" onSubmit={handleCreateProject}>
                <label className="form-field">
                  <span className="form-label">Client</span>
                  <input
                    className="form-input"
                    value={createForm.client}
                    onChange={(event) => setCreateForm({ ...createForm, client: event.target.value })}
                    required
                  />
                </label>

                <label className="form-field">
                  <span className="form-label">Projektname</span>
                  <input
                    className="form-input"
                    value={createForm.projectName}
                    onChange={(event) =>
                      setCreateForm({ ...createForm, projectName: event.target.value })
                    }
                    required
                  />
                </label>

                <label className="form-field">
                  <span className="form-label">Währung</span>
                  <select
                    className="form-input"
                    value={createForm.currency}
                    onChange={(event) => setCreateForm({ ...createForm, currency: event.target.value })}
                    required
                  >
                    <option value="EUR">EUR</option>
                    <option value="USD">USD</option>
                    <option value="GBP">GBP</option>
                    <option value="CHF">CHF</option>
                  </select>
                </label>

                <label className="form-field">
                  <span className="form-label">Bewertungsstichtag</span>
                  <input
                    className="form-input"
                    type="date"
                    value={createForm.valuationDate}
                    onChange={(event) =>
                      setCreateForm({ ...createForm, valuationDate: event.target.value })
                    }
                    required
                  />
                </label>

                <label className="form-field">
                  <span className="form-label">Reporting-Sprache</span>
                  <select
                    className="form-input"
                    value={createForm.reportingLanguage}
                    onChange={(event) =>
                      setCreateForm({ ...createForm, reportingLanguage: event.target.value })
                    }
                    required
                  >
                    <option value="de">Deutsch</option>
                    <option value="en">Englisch</option>
                  </select>
                </label>

                <div className="admin-modal-actions">
                  <button type="button" className="btn btn-secondary" onClick={() => setCreateOpen(false)}>
                    Abbrechen
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={createProject.isPending}>
                    {createProject.isPending ? 'Speichern…' : 'Projekt anlegen'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
