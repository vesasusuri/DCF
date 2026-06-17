import type { AuditLog } from './api'

export const ACTION_LABELS: Record<string, string> = {
  login: 'Anmeldung',
  logout: 'Abmeldung',
  'page.view': 'Seitenaufruf',
  'api.request': 'API-Anfrage',
  'models.list': 'DCF-Modelle abgerufen',
  'user.created': 'Benutzer angelegt',
  'user.updated': 'Benutzer aktualisiert',
}

export function actionLabel(action: string) {
  return ACTION_LABELS[action] ?? action.replaceAll('.', ' · ')
}

export function actionBadgeClass(action: string) {
  if (action === 'login') return 'badge-success'
  if (action === 'logout') return 'badge-neutral'
  if (action === 'page.view') return 'badge-info'
  if (action === 'api.request') return 'badge-neutral'
  if (action.startsWith('user.')) return 'badge-warning'
  if (action.startsWith('models.')) return 'badge-info'
  return 'badge-neutral'
}

export function areaLabel(log: AuditLog) {
  const area = log.details.area
  if (area === 'admin') return 'Admin'
  if (area === 'workbench') return 'Workbench'
  if (log.action.startsWith('user.')) return 'Admin'
  if (log.action === 'api.request') return 'API'
  if (log.action === 'login' || log.action === 'logout') return 'Auth'
  return 'Plattform'
}

export function formatAuditDetails(log: AuditLog) {
  const parts: string[] = []
  const { details, resource, action } = log

  if (typeof details.title === 'string') {
    parts.push(details.title)
  } else if (resource) {
    parts.push(resource)
  }

  if (action === 'api.request') {
    if (details.method && details.path) {
      parts.push(`${String(details.method)} ${String(details.path)}`)
    }
    if (details.status_code !== undefined) {
      parts.push(`HTTP ${String(details.status_code)}`)
    }
  }

  if (action === 'models.list' && details.count !== undefined) {
    parts.push(`${String(details.count)} Einträge`)
  }

  if (details.role) {
    parts.push(`Rolle: ${details.role === 'admin' ? 'Admin' : 'Benutzer'}`)
  }
  if (details.full_name) {
    parts.push(`Name: ${String(details.full_name)}`)
  }
  if (details.password_changed) {
    parts.push('Passwort geändert')
  }

  return parts.length > 0 ? parts.join(' · ') : '—'
}
