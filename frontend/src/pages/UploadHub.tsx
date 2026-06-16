import { useState } from 'react'
import { ArrowDownToLine } from 'lucide-react'
import { PageWrapper } from '../components/layout/MainLayout'

const filterTabs = ['Rent rolls', 'Leases', 'Fact sheets', 'Capex', 'Market']

const checklistItems = [
  { label: 'Rent Roll (Excel)', done: true },
  { label: 'Property Schedule', done: true },
  { label: 'Lease-PDFs (42)', done: true },
  { label: 'Capex-Plan', done: false },
  { label: 'Energieausweise', done: false },
  { label: 'Markt-Annahmen', done: false },
]

const classifiedFiles = [
  {
    name: 'RentRoll_NRW_2026.xlsx',
    type: 'Rent roll',
    property: 'Portfolio-weit',
    confidence: '0.99',
    status: 'OK' as const,
    fileType: 'XLS' as const,
  },
  {
    name: 'Lease_DC-Hannover_18.pdf',
    type: 'Lease',
    property: 'DC Hannover-Süd',
    confidence: '0.97',
    status: 'OK' as const,
    fileType: 'PDF' as const,
  },
  {
    name: 'Factsheet_Koeln-Nord.pdf',
    type: 'Fact sheet',
    property: 'Logistikpark Köln-Nord',
    confidence: '0.95',
    status: 'OK' as const,
    fileType: 'PDF' as const,
  },
  {
    name: 'scan_2026_0412.pdf',
    type: '— unklar',
    property: 'kein Treffer',
    confidence: '0.28',
    status: 'Fehlt' as const,
    fileType: 'PDF' as const,
    error: true,
  },
  {
    name: 'Capex_Duesseldorf.xlsx',
    type: 'Capex',
    property: 'Urban Logistics Düsseldorf',
    confidence: '0.64',
    status: 'Review' as const,
    fileType: 'XLS' as const,
    warning: true,
  },
  {
    name: 'Energie_Essen_LI.pdf',
    type: 'Energieausweis',
    property: 'Light Industrial Essen',
    confidence: '0.92',
    status: 'OK' as const,
    fileType: 'PDF' as const,
  },
]

const statusBadge: Record<string, string> = {
  OK: 'badge-success',
  Fehlt: 'badge-error',
  Review: 'badge-warning',
}

export function UploadHub() {
  const [activeFilter, setActiveFilter] = useState('Rent rolls')
  const doneCount = checklistItems.filter((i) => i.done).length

  return (
    <PageWrapper
      breadcrumbs={[
        { label: 'Colliers Germany' },
        { label: 'LI Portfolio NRW' },
        { label: 'Upload', current: true },
      ]}
    >
      <div className="upload-page">
        <div className="upload-header">
          <div>
            <div className="page-eyebrow upload-eyebrow">S02 · UPLOAD</div>
            <h1 className="page-title upload-title">Upload-Hub</h1>
          </div>
          <div className="pill-tabs">
            {filterTabs.map((tab) => (
              <button
                key={tab}
                className={`pill-tab${activeFilter === tab ? ' active' : ''}`}
                onClick={() => setActiveFilter(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="upload-layout">
          <div>
            <div className="dropzone">
              <div className="dropzone-icon-wrap">
                <ArrowDownToLine size={24} strokeWidth={1.75} />
              </div>
              <div className="dropzone-title">Portfolio-Dateien hierher ziehen</div>
              <div className="dropzone-sub">
                Excel-Rent-Rolls · Lease-PDFs · Property-Factsheets ·
                <br />
                Capex-Pläne · Energieausweise
              </div>
              <button className="btn btn-primary">Dateien auswählen</button>
            </div>

            <div className="upload-progress-list">
              <div className="upload-progress-row">
                <span className="upload-progress-name">RentRoll_NRW_2026.xlsx</span>
                <div className="progress-bar">
                  <div className="progress-bar-fill green" style={{ width: '100%' }} />
                </div>
                <span className="upload-progress-pct complete">100%</span>
              </div>
              <div className="upload-progress-row">
                <span className="upload-progress-name">Lease-Paket (42 PDFs)</span>
                <div className="progress-bar">
                  <div className="progress-bar-fill blue" style={{ width: '72%' }} />
                </div>
                <span className="upload-progress-pct in-progress">72%</span>
              </div>
            </div>
          </div>

          <div className="card upload-checklist-card">
            <div className="upload-checklist-header">
              <div className="upload-checklist-title-block">
                <div className="card-title-row">
                  <div className="card-accent-bar" />
                  <div className="card-title">Upload-Checkliste</div>
                </div>
                <div className="card-subtitle">Pflicht-Dokumente</div>
              </div>
              <span className="checklist-fraction">
                {doneCount} / {checklistItems.length}
              </span>
            </div>
            <ul className="checklist">
              {checklistItems.map((item) => (
                <li
                  key={item.label}
                  className={`checklist-item${item.done ? ' done' : ' pending'}`}
                >
                  {item.done ? (
                    <span className="checklist-icon-done">✓</span>
                  ) : (
                    <span className="checklist-icon-pending" />
                  )}
                  {item.label}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="card upload-files-card">
          <div className="upload-checklist-title-block">
            <div className="card-title-row">
              <div className="card-accent-bar" />
              <div className="card-title">Klassifizierte Dateien</div>
            </div>
            <div className="card-subtitle">
              Auto-Klassifizierung · 1 ohne Treffer · 1 niedrige Konfidenz
            </div>
          </div>
          <table className="upload-files-table">
            <thead>
              <tr>
                <th>Datei</th>
                <th>Erkannter Typ</th>
                <th>Property-Match</th>
                <th className="col-confidence">Konf.</th>
                <th className="col-status">Status</th>
              </tr>
            </thead>
            <tbody>
              {classifiedFiles.map((file) => (
                <tr key={file.name}>
                  <td>
                    <div className="file-cell">
                      <span className="file-type-badge">{file.fileType}</span>
                      {file.name}
                    </div>
                  </td>
                  <td className={file.error ? 'text-error' : undefined}>{file.type}</td>
                  <td className={file.error ? 'text-error' : undefined}>{file.property}</td>
                  <td
                    className={`col-confidence confidence-mono${file.warning || file.error ? (file.error ? ' text-error' : ' text-warning') : ''}`}
                  >
                    {file.confidence}
                  </td>
                  <td className="col-status">
                    <span className={`badge ${statusBadge[file.status]}`}>{file.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  )
}
