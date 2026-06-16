import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Upload, Check, FileSpreadsheet, FileText } from 'lucide-react'
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
    icon: 'excel' as const,
  },
  {
    name: 'Lease_DC-Hannover_18.pdf',
    type: 'Lease',
    property: 'DC Hannover-Süd',
    confidence: '0.97',
    status: 'OK' as const,
    icon: 'pdf' as const,
  },
  {
    name: 'Factsheet_Koeln-Nord.pdf',
    type: 'Fact sheet',
    property: 'Logistikpark Köln-Nord',
    confidence: '0.95',
    status: 'OK' as const,
    icon: 'pdf' as const,
  },
  {
    name: 'scan_2026_0412.pdf',
    type: '— unklar',
    property: 'kein Treffer',
    confidence: '0.28',
    status: 'Fehlt' as const,
    icon: 'pdf' as const,
    error: true,
  },
  {
    name: 'Capex_Duesseldorf.xlsx',
    type: 'Capex',
    property: 'Urban Logistics Düsseldorf',
    confidence: '0.64',
    status: 'Review' as const,
    icon: 'excel' as const,
    warning: true,
  },
  {
    name: 'Energie_Essen_LI.pdf',
    type: 'Energieausweis',
    property: 'Light Industrial Essen',
    confidence: '0.92',
    status: 'OK' as const,
    icon: 'pdf' as const,
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
      <div className="page-eyebrow">S02 · UPLOAD</div>
      <div className="page-header">
        <h1 className="page-title">Upload-Hub</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
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
          <Link to="/upload/mapping" className="btn btn-primary btn-sm">
            Daten mappen →
          </Link>
        </div>
      </div>

      <div className="upload-layout">
        <div>
          <div className="dropzone">
            <div className="dropzone-icon">
              <Upload size={36} strokeWidth={1.5} />
            </div>
            <div className="dropzone-title">Portfolio-Dateien hierher ziehen</div>
            <div className="dropzone-sub">
              Excel (.xlsx), PDF, CSV · max. 50 MB pro Datei
            </div>
            <button className="btn btn-primary" style={{ marginTop: 8 }}>
              Dateien auswählen
            </button>
          </div>

          <div className="upload-progress-list">
            <div className="upload-progress-item">
              <div className="upload-progress-header">
                <span className="upload-progress-name">RentRoll_NRW_2026.xlsx</span>
                <span className="upload-progress-pct">100%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill green" style={{ width: '100%' }} />
              </div>
            </div>
            <div className="upload-progress-item">
              <div className="upload-progress-header">
                <span className="upload-progress-name">Lease-Paket (42 PDFs)</span>
                <span className="upload-progress-pct">72%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill blue" style={{ width: '72%' }} />
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title-row">
                <div className="card-accent-bar" />
                <div className="card-title">Upload-Checkliste</div>
              </div>
            </div>
            <span className="checklist-fraction">
              {doneCount} / {checklistItems.length}
            </span>
          </div>
          <div className="card-body">
            <ul className="checklist">
              {checklistItems.map((item) => (
                <li key={item.label} className="checklist-item">
                  {item.done ? (
                    <Check size={16} className="checklist-icon-done" />
                  ) : (
                    <span className="checklist-icon-pending" />
                  )}
                  {item.label}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title-row">
            <div className="card-accent-bar" />
            <div className="card-title">Klassifizierte Dateien</div>
          </div>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Datei</th>
              <th>Erkannter Typ</th>
              <th>Property-Match</th>
              <th>Konf.</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {classifiedFiles.map((file) => (
              <tr key={file.name}>
                <td>
                  <div className="file-cell">
                    {file.icon === 'excel' ? (
                      <FileSpreadsheet size={18} className="file-icon" color="#16a34a" />
                    ) : (
                      <FileText size={18} className="file-icon" color="#c32b1e" />
                    )}
                    {file.name}
                  </div>
                </td>
                <td className={file.error ? 'text-error' : undefined}>{file.type}</td>
                <td className={file.error ? 'text-error' : undefined}>{file.property}</td>
                <td className={file.warning || file.error ? (file.error ? 'text-error' : 'text-warning') : undefined}>
                  {file.confidence}
                </td>
                <td>
                  <span className={`badge ${statusBadge[file.status]}`}>{file.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageWrapper>
  )
}
