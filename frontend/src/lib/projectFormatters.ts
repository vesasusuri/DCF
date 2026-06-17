import type { LatestRun, ProjectStatus, ProjectSummary } from '../types/project'

const STATUS_LABELS: Record<ProjectStatus, string> = {
  draft: 'Entwurf',
  test: 'Prüfung',
  ready: 'Fertig',
  active: 'Aktiv',
  archived: 'Archiviert',
}

const STATUS_BADGE_CLASS: Record<ProjectStatus, string> = {
  draft: 'badge-neutral',
  test: 'badge-warning',
  ready: 'badge-success',
  active: 'badge-success',
  archived: 'badge-neutral',
}

export function getProjectStatusLabel(status: ProjectStatus): string {
  return STATUS_LABELS[status] ?? status
}

export function getProjectStatusBadgeClass(status: ProjectStatus): string {
  return STATUS_BADGE_CLASS[status] ?? 'badge-neutral'
}

function formatRelativeTime(isoDate: string): string {
  const date = new Date(isoDate)
  const diffMs = Date.now() - date.getTime()
  const diffMinutes = Math.floor(diffMs / 60_000)
  const diffHours = Math.floor(diffMs / 3_600_000)
  const diffDays = Math.floor(diffMs / 86_400_000)

  if (diffMinutes < 1) return 'gerade eben'
  if (diffMinutes < 60) return `vor ${diffMinutes} Min.`
  if (diffHours < 24) return `vor ${diffHours} Std.`
  if (diffDays === 1) return 'gestern'
  if (diffDays < 7) return `vor ${diffDays} Tagen`
  return date.toLocaleDateString('de-DE')
}

export function formatLatestRunDetail(status: ProjectStatus, latestRun: LatestRun | null): string {
  if (!latestRun?.runNumber) {
    return status === 'draft' ? 'Entwurf · kein Lauf' : 'Kein Lauf'
  }

  const timestamp = latestRun.completedAt ?? latestRun.createdAt
  const suffix = timestamp ? ` · ${formatRelativeTime(timestamp)}` : ''
  return `Lauf #${latestRun.runNumber}${suffix}`
}

export function formatProjectSubtitle(project: ProjectSummary): string {
  const client = project.clientName ?? '—'
  const created = project.createdAt
    ? new Date(project.createdAt).toLocaleDateString('de-DE')
    : '—'
  return `${client} · ${project.assetCount} Assets · Erstellt ${created}`
}

export function formatProjectStatusDetail(project: ProjectSummary): string {
  const runDetail = formatLatestRunDetail(project.status, project.latestRun)
  const updated = project.updatedAt
    ? new Date(project.updatedAt).toLocaleDateString('de-DE')
    : '—'
  return `${runDetail} · Aktualisiert ${updated}`
}

export function formatDateTime(isoDate: string | null): string {
  if (!isoDate) return '—'
  return new Date(isoDate).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function countUniqueTeams(projects: ProjectSummary[]): number {
  const teams = new Set(
    projects.map((project) => project.assignedTeam).filter((team): team is string => Boolean(team)),
  )
  return teams.size
}
