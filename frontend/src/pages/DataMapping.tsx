import { Check } from 'lucide-react'
import { PageWrapper } from '../components/layout/MainLayout'

const mappingRows = [
  { source: 'Mieter', target: 'tenant', tag: 'auto' as const },
  { source: 'Fläche', target: 'area_sqm', tag: 'auto' as const },
  { source: 'Miete p.a.', target: 'rent_pa', tag: 'auto' as const },
  { source: 'Laufzeit Ende', target: 'expiry', tag: 'prüfen' as const },
  { source: 'Index', target: '— nicht gemappt', tag: 'mappen' as const, error: true },
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
  },
]

const tagClass = { auto: 'auto', prüfen: 'check', mappen: 'map' }

const steps = [
  { label: 'Quelle', done: true },
  { label: 'Spalten mappen', active: true },
  { label: 'Validieren', done: false },
  { label: 'Bestätigen', done: false },
]

export function DataMapping() {
  return (
    <PageWrapper
      breadcrumbs={[
        { label: '…' },
        { label: 'Upload' },
        { label: 'Daten mappen', current: true },
      ]}
    >
      <div className="page-eyebrow">S03 · MAPPING</div>
      <div className="page-header">
        <h1 className="page-title">Daten-Mapping-Assistent</h1>
        <div className="page-actions">
          <button className="btn btn-secondary">Verwerfen</button>
          <button className="btn btn-primary">Weiter: Validieren →</button>
        </div>
      </div>

      <div className="stepper">
        {steps.map((step, i) => (
          <div key={step.label} style={{ display: 'contents' }}>
            <div className={`step${step.active ? ' active' : ''}${step.done ? ' done' : ''}`}>
              <div className="step-circle">
                {step.done ? <Check size={14} /> : i + 1}
              </div>
              {step.label}
            </div>
            {i < steps.length - 1 && (
              <div className={`step-line${step.done ? ' done' : ''}`} />
            )}
          </div>
        ))}
      </div>

      <div className="mapping-layout">
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title-row">
                <div className="card-accent-bar" />
                <div className="card-title">Spalten-Mapping</div>
              </div>
              <div className="card-subtitle" style={{ marginLeft: 11 }}>
                Quell-Spalte → kanonisches Feld · Auto-Vorschlag
              </div>
            </div>
            <button className="btn btn-secondary btn-sm">Vorlage speichern</button>
          </div>
          <div className="card-body">
            {mappingRows.map((row) => (
              <div key={row.source} className="mapping-row">
                <span className="mapping-source">&quot;{row.source}&quot;</span>
                <span className="mapping-arrow">→</span>
                <span className={`mapping-target${row.error ? ' error' : ''}`}>
                  {row.target}
                </span>
                <span className={`mapping-tag ${tagClass[row.tag]}`}>{row.tag}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title-row">
                <div className="card-accent-bar" />
                <div className="card-title">Live-Vorschau &amp; Validierung</div>
              </div>
              <div className="card-subtitle" style={{ marginLeft: 11 }}>
                Bewertungskritische Felder zuerst
              </div>
            </div>
            <div className="validation-summary">
              <span className="validation-error">1 Fehler</span>
              <span className="validation-warning">1 Warnung</span>
            </div>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 24 }} />
                <th>Tenant</th>
                <th>Fläche m²</th>
                <th>Miete p.a.</th>
                <th>Expiry</th>
                <th>Index</th>
              </tr>
            </thead>
            <tbody>
              {previewRows.map((row) => (
                <tr key={row.tenant}>
                  <td>
                    <span className={`status-dot ${row.status}`} />
                  </td>
                  <td style={{ color: 'var(--color-text)', fontWeight: 500 }}>{row.tenant}</td>
                  <td>{row.area}</td>
                  <td>{row.rent}</td>
                  <td className={row.expiryError ? 'text-error' : undefined}>{row.expiry}</td>
                  <td>{row.index}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  )
}
