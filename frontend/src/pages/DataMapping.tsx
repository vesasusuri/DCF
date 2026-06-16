import { PageWrapper } from '../components/layout/MainLayout'

const mappingRows = [
  { source: 'Mieter', target: 'tenant', tag: 'auto' as const },
  { source: 'Fläche m²', target: 'unit.area', tag: 'auto' as const },
  { source: 'Miete p.a.', target: 'passing_rent', tag: 'auto' as const },
  { source: 'Ende', target: 'lease.expiry', tag: 'prüfen' as const },
  { source: 'Index', target: '— nicht gemappt', tag: 'mappen' as const, error: true },
  { source: 'Staffel', target: 'rent_step', tag: 'auto' as const },
]

const previewRows = [
  {
    status: 'green' as const,
    tenant: 'Möbel Direkt',
    area: '6.250',
    rent: '412.000',
    expiry: '2030-01-31',
    index: 'CPI 70%',
  },
  {
    status: 'green' as const,
    tenant: 'TechParts AG',
    area: '1.920',
    rent: '149.000',
    expiry: '2031-06-30',
    index: 'CPI 100%',
  },
  {
    status: 'orange' as const,
    tenant: 'Spedition Nord KG',
    area: '3.480',
    rent: '228.500',
    expiry: '31.12.2027',
    expiryError: true,
    index: '—',
    indexWarning: true,
  },
]

const tagClass = { auto: 'auto', prüfen: 'check', mappen: 'map' }

const steps = [
  { label: 'Quelle', state: 'done' as const },
  { label: 'Spalten mappen', state: 'active' as const },
  { label: 'Validieren', state: 'pending' as const },
  { label: 'Bestätigen', state: 'pending' as const },
]

export function DataMapping() {
  return (
    <PageWrapper
      breadcrumbs={[
        { label: 'Upload' },
        { label: 'Daten mappen', current: true },
      ]}
    >
      <div className="mapping-page">
        <div className="mapping-header">
          <div>
            <div className="page-eyebrow mapping-eyebrow">S03 · MAPPING</div>
            <h1 className="page-title mapping-title">Daten-Mapping-Assistent</h1>
          </div>
          <div className="page-actions">
            <button type="button" className="btn btn-secondary">
              Verwerfen
            </button>
            <button type="button" className="btn btn-primary">
              Weiter: Validieren →
            </button>
          </div>
        </div>

        <div className="stepper">
          {steps.map((step, i) => (
            <div key={step.label} className="stepper-segment">
              <div className={`step ${step.state}`}>
                <div className="step-circle">
                  {step.state === 'done' ? '✓' : i + 1}
                </div>
                {step.label}
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`step-line${step.state === 'done' ? ' done' : ''}`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="mapping-layout">
          <div className="card mapping-card">
            <div className="mapping-card-header">
              <div className="mapping-card-title-block">
                <div className="card-title-row">
                  <div className="card-accent-bar" />
                  <div className="card-title">Spalten-Mapping</div>
                </div>
                <div className="card-subtitle">
                  Quell-Spalte → kanonisches Feld · Auto-Vorschlag
                </div>
              </div>
              <button type="button" className="btn btn-secondary btn-sm">
                Vorlage speichern
              </button>
            </div>
            <div className="mapping-rows">
              {mappingRows.map((row) => (
                <div key={row.source} className="mapping-row">
                  <span className="mapping-source">&quot;{row.source}&quot;</span>
                  <span className="mapping-arrow">→</span>
                  <span className={`mapping-target${row.error ? ' error' : ''}`}>
                    {row.target}
                    <span className="mapping-target-chevron">▾</span>
                  </span>
                  <span className={`mapping-tag ${tagClass[row.tag]}`}>{row.tag}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card mapping-card">
            <div className="mapping-card-header">
              <div className="mapping-card-title-block">
                <div className="card-title-row">
                  <div className="card-accent-bar" />
                  <div className="card-title">Live-Vorschau &amp; Validierung</div>
                </div>
                <div className="card-subtitle">Bewertungskritische Felder zuerst</div>
              </div>
              <div className="validation-summary">
                <span className="validation-error">1 Fehler</span>
                <span className="validation-warning">1 Warnung</span>
              </div>
            </div>
            <table className="mapping-preview-table">
              <thead>
                <tr>
                  <th>Tenant</th>
                  <th>Fläche m²</th>
                  <th>Miete p.a.</th>
                  <th>Expiry</th>
                  <th>Index</th>
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row) => (
                  <tr key={row.tenant} className={`status-${row.status}`}>
                    <td>
                      <div className="tenant-cell">
                        <span className={`status-dot ${row.status}`} />
                        <span className="tenant-name">{row.tenant}</span>
                      </div>
                    </td>
                    <td>{row.area}</td>
                    <td>{row.rent}</td>
                    <td className={row.expiryError ? 'text-error' : undefined}>
                      {row.expiry}
                    </td>
                    <td className={row.indexWarning ? 'text-warning' : undefined}>
                      {row.index}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
