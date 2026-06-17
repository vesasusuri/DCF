import { api, type CreateAuditLogPayload } from './api'

const PAGE_TITLES: Record<string, string> = {
  '/projects': 'Projekte',
  '/upload': 'Upload',
  '/upload/mapping': 'Datenzuordnung',
  '/data-review/extraction': 'Extraktionsprüfung',
  '/assumptions': 'Annahmen',
  '/runs': 'Bewertungsläufe',
  '/results': 'Ergebnisse',
  '/dashboards': 'Dashboards',
  '/reports': 'Berichte',
  '/admin': 'Admin Übersicht',
  '/admin/users': 'Benutzerverwaltung',
  '/admin/settings': 'Systemeinstellungen',
  '/admin/audit': 'Audit & Compliance',
  '/admin/security': 'Sicherheit',
  '/login': 'Anmeldung',
}

let lastPageLog: { path: string; at: number } | null = null

function pageTitle(path: string) {
  if (PAGE_TITLES[path]) return PAGE_TITLES[path]
  const match = Object.entries(PAGE_TITLES).find(([route]) => path.startsWith(`${route}/`))
  return match?.[1] ?? path
}

export function recordPlatformEvent(payload: CreateAuditLogPayload) {
  void api.audit.recordEvent(payload).catch(() => undefined)
}

export function recordPageView(path: string) {
  const now = Date.now()
  if (lastPageLog?.path === path && now - lastPageLog.at < 1000) return
  lastPageLog = { path, at: now }

  recordPlatformEvent({
    action: 'page.view',
    resource: path,
    details: {
      title: pageTitle(path),
      area: path.startsWith('/admin') ? 'admin' : 'workbench',
    },
  })
}
