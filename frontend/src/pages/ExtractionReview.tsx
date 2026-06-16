import { useState } from 'react'
import { PageWrapper } from '../components/layout/MainLayout'

const filterTabs = ['Alle', 'Niedrige Konfidenz', 'Kritische Terme', 'Konflikte']

const extractionFields = [
  {
    label: 'Tenant',
    value: 'Logistik GmbH',
    confidence: 0.98,
    level: 'high' as const,
    action: 'Freigeben',
    actionClass: 'approve' as const,
  },
  {
    label: 'Passing Rent',
    value: '€ 412.000 p.a.',
    confidence: 0.95,
    level: 'high' as const,
    action: 'Freigeben',
    actionClass: 'approve' as const,
  },
  {
    label: 'Indexation',
    value: 'CPI, 70% Pass-through',
    confidence: 0.61,
    level: 'medium' as const,
    action: 'Bearbeiten',
    actionClass: 'edit' as const,
  },
  {
    label: 'Break Option',
    value: 'nicht gefunden',
    confidence: 0.3,
    level: 'low' as const,
    action: 'Ergänzen',
    actionClass: 'complete' as const,
  },
]

const pdfLines = [90, 70, 85, 60, 75, 50, 80, 65, 55, 70, 45, 60]

export function ExtractionReview() {
  const [activeTab, setActiveTab] = useState('Alle')

  return (
    <PageWrapper
      breadcrumbs={[
        { label: '…' },
        { label: 'Datenprüfung' },
        { label: 'KI-Extraktion', current: true },
      ]}
    >
      <div className="extraction-header">
        <div>
          <h1 className="page-title">KI-Extraktions-Review</h1>
          <div className="tabs" style={{ marginTop: 12 }}>
            {filterTabs.map((tab) => (
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
        <div className="lease-counter">
          Lease <strong>18</strong> / 42
        </div>
      </div>

      <div className="extraction-layout">
        <div className="pdf-viewer">
          <div className="pdf-viewer-header">
            <span>Lease-PDF — Seite 3</span>
            <span>Evidence-Linking</span>
          </div>
          <div className="pdf-page">
            {pdfLines.slice(0, 4).map((w, i) => (
              <div key={i} className="pdf-line" style={{ width: `${w}%` }} />
            ))}
            <div className="pdf-highlight">
              <div className="pdf-highlight-title">§ 4 Mietzins &amp; Indexierung</div>
              <div className="pdf-line" style={{ width: '90%' }} />
              <div className="pdf-line" style={{ width: '75%' }} />
            </div>
            {pdfLines.slice(4).map((w, i) => (
              <div key={i + 4} className="pdf-line" style={{ width: `${w}%` }} />
            ))}
          </div>
          <div className="pdf-viewer-footer">
            Klick auf ein Feld rechts markiert die Belegstelle hier.
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title-row">
                <div className="card-accent-bar" />
                <div className="card-title">Extrahierte Felder</div>
              </div>
              <div className="card-subtitle" style={{ marginLeft: 11 }}>
                Lease 18 · Logistik GmbH
              </div>
            </div>
            <span className="ki-badge">KI schlägt vor</span>
          </div>
          <div className="card-body">
            {extractionFields.map((field) => (
              <div key={field.label} className="extraction-field">
                <div className="extraction-field-label">{field.label}</div>
                <div className="extraction-field-value">{field.value}</div>
                <div className="extraction-field-row">
                  <div className="confidence-bar">
                    <div
                      className={`confidence-bar-fill ${field.level}`}
                      style={{ width: `${field.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-value">{field.confidence.toFixed(2)}</span>
                  <button className={`field-action-btn ${field.actionClass}`}>
                    {field.action}
                  </button>
                </div>
              </div>
            ))}

            <div className="extraction-footer">
              <p className="extraction-footer-note">
                Gate: freigegebene Werte fließen erst nach Bestätigung in die Berechnung.
              </p>
              <div className="extraction-footer-actions">
                <button className="btn btn-secondary">Alle ablehnen</button>
                <button className="btn btn-primary">Lease freigeben</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
