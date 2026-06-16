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
    error: true,
  },
  {
    label: 'Service Charge',
    value: 'umlagefähig',
    confidence: 0.91,
    level: 'high' as const,
    action: 'Freigeben',
    actionClass: 'approve' as const,
  },
  {
    label: 'Lease Expiry',
    value: '31.03.2029',
    confidence: 0.88,
    level: 'high' as const,
    action: 'Freigeben',
    actionClass: 'approve' as const,
  },
]

const pdfLines = [
  349, 404, 298, '100%', 255, 383, 323, '100%', 358, 281, 392, 306,
]

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
      <div className="extraction-page">
        <div className="extraction-header-bar">
          <div className="extraction-header-title">
            <div className="page-eyebrow extraction-eyebrow">S04 · KI-REVIEW</div>
            <h1 className="page-title extraction-title">KI-Extraktions-Review</h1>
          </div>

          <div className="extraction-tabs">
            {filterTabs.map((tab) => (
              <button
                key={tab}
                type="button"
                className={`extraction-tab${activeTab === tab ? ' active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="lease-counter">
            Lease <strong>18 / 42</strong>
          </div>
        </div>

        <div className="extraction-layout">
          <div className="pdf-viewer">
            <div className="pdf-viewer-header">
              <span>Lease-PDF — Seite 3</span>
              <span>Evidence-Linking</span>
            </div>
            <div className="pdf-page">
              {pdfLines.slice(0, 5).map((w, i) => (
                <div
                  key={i}
                  className="pdf-line"
                  style={{ width: typeof w === 'number' ? `${(w / 430) * 100}%` : w }}
                />
              ))}
              <div className="pdf-highlight">
                <div className="pdf-highlight-title">§ 4 Mietzins &amp; Indexierung</div>
                <div className="pdf-line" style={{ width: '100%' }} />
                <div className="pdf-line" style={{ width: '81%' }} />
              </div>
              {pdfLines.slice(5).map((w, i) => (
                <div
                  key={i + 5}
                  className="pdf-line"
                  style={{ width: typeof w === 'number' ? `${(w / 430) * 100}%` : w }}
                />
              ))}
            </div>
            <div className="pdf-viewer-footer">
              Klick auf ein Feld rechts markiert die Belegstelle hier.
            </div>
          </div>

          <div className="extraction-fields-card">
            <div className="extraction-fields-header">
              <div className="mapping-card-title-block">
                <div className="card-title-row">
                  <div className="card-accent-bar" />
                  <div className="card-title">Extrahierte Felder</div>
                </div>
                <div className="card-subtitle">Lease 18 · Logistik GmbH</div>
              </div>
              <span className="ki-badge">KI schlägt vor</span>
            </div>

            <div className="extraction-fields-body">
              {extractionFields.map((field) => (
                <div key={field.label} className="extraction-field">
                  <div className="extraction-field-info">
                    <div className="extraction-field-label">{field.label}</div>
                    <div
                      className={`extraction-field-value${field.error ? ' error' : ''}`}
                    >
                      {field.value}
                    </div>
                  </div>
                  <div className="extraction-field-confidence">
                    <div className="confidence-bar">
                      <div
                        className={`confidence-bar-fill ${field.level}`}
                        style={{ width: `${field.confidence * 100}%` }}
                      />
                    </div>
                    <span className={`confidence-value ${field.level}`}>
                      {field.confidence.toFixed(2)}
                    </span>
                  </div>
                  <div className="extraction-field-action">
                    <button
                      type="button"
                      className={`field-action-btn ${field.actionClass}`}
                    >
                      {field.action}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="extraction-footer">
              <p className="extraction-footer-note">
                <strong>Gate:</strong> freigegebene Werte fließen erst nach
                Bestätigung in die Berechnung.
              </p>
              <div className="extraction-footer-actions">
                <button type="button" className="btn btn-secondary">
                  Alle ablehnen
                </button>
                <button type="button" className="btn btn-primary">
                  Lease freigeben
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
