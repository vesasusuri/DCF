import { Search, ChevronDown } from 'lucide-react'

type TopHeaderProps = {
  breadcrumbs: { label: string; current?: boolean }[]
}

export function TopHeader({ breadcrumbs }: TopHeaderProps) {
  return (
    <header className="top-header">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        {breadcrumbs.map((crumb, i) => (
          <span key={i}>
            {i > 0 && <span> › </span>}
            <span className={crumb.current ? 'current' : undefined}>
              {crumb.label}
            </span>
          </span>
        ))}
      </nav>

      <div className="header-actions">
        <div className="search-input">
          <Search size={14} />
          <span>Suchen…</span>
        </div>
        <div className="scenario-select">
          Szenario: <strong>Basis</strong>
          <ChevronDown size={14} />
        </div>
        <div className="user-avatar" title="MB">MB</div>
      </div>
    </header>
  )
}
