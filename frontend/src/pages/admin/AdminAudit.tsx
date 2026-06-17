import { useCallback, useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { AdminPageWrapper } from '../../components/layout/AdminLayout'
import { api, AUDIT_PAGE_SIZE, type AuditLog } from '../../lib/api'
import {
  actionBadgeClass,
  actionLabel,
  areaLabel,
  formatAuditDetails,
} from '../../lib/auditDisplay'

function formatDate(value: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function AdminAudit() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadLogs = useCallback(async (targetPage: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.admin.listLogs(targetPage, AUDIT_PAGE_SIZE)
      setLogs(data.items)
      setPage(data.page)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Audit-Logs konnten nicht geladen werden.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadLogs(1)
  }, [loadLogs])

  const rangeStart = total === 0 ? 0 : (page - 1) * AUDIT_PAGE_SIZE + 1
  const rangeEnd = Math.min(page * AUDIT_PAGE_SIZE, total)

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

          <div className="page-actions">
            <button type="button" className="btn btn-secondary" onClick={() => void loadLogs(page)}>
              Aktualisieren
            </button>
          </div>
        </div>

        {error && <div className="login-error admin-banner-error">{error}</div>}

        <div className="card admin-table-card">
          <div className="admin-table-header">
            <div>
              <div className="card-section-title">Plattform-Aktivitätsprotokoll</div>
              <div className="card-section-sub">
                {total > 0
                  ? `${total} Ereignisse plattformweit · Seite ${page} von ${totalPages}`
                  : 'Anmeldungen, Seitenaufrufe, API-Aufrufe und Admin-Aktionen'}
              </div>
            </div>
          </div>

          {loading ? (
            <div className="admin-empty-state">Protokoll wird geladen…</div>
          ) : logs.length === 0 ? (
            <div className="admin-empty-state">
              Noch keine Einträge. Nutzen Sie die Plattform — Aktivitäten werden automatisch
              protokolliert.
            </div>
          ) : (
            <>
              <div className="admin-table-wrap">
                <table className="data-table admin-table">
                  <thead>
                    <tr>
                      <th>Zeitpunkt</th>
                      <th>Bereich</th>
                      <th>Aktion</th>
                      <th>Benutzer</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id}>
                        <td className="admin-log-time">{formatDate(log.created_at)}</td>
                        <td>
                          <span className="badge badge-neutral">{areaLabel(log)}</span>
                        </td>
                        <td>
                          <span className={`badge ${actionBadgeClass(log.action)}`}>
                            {actionLabel(log.action)}
                          </span>
                        </td>
                        <td>
                          <div className="admin-log-actor">{log.actor_name ?? 'System'}</div>
                          <div className="admin-log-email">{log.actor_email ?? '—'}</div>
                        </td>
                        <td className="admin-log-details">{formatAuditDetails(log)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="admin-pagination">
                  <div className="admin-pagination-meta">
                    Zeige {rangeStart}–{rangeEnd} von {total}
                  </div>
                  <div className="admin-pagination-controls">
                    <button
                      type="button"
                      className="btn btn-secondary admin-pagination-btn"
                      disabled={page <= 1}
                      onClick={() => void loadLogs(page - 1)}
                      aria-label="Vorherige Seite"
                    >
                      <ChevronLeft size={16} />
                      Zurück
                    </button>
                    <span className="admin-pagination-pages">
                      Seite {page} / {totalPages}
                    </span>
                    <button
                      type="button"
                      className="btn btn-secondary admin-pagination-btn"
                      disabled={page >= totalPages}
                      onClick={() => void loadLogs(page + 1)}
                      aria-label="Nächste Seite"
                    >
                      Weiter
                      <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </AdminPageWrapper>
  )
}
