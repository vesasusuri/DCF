import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Projekte', code: 'S01', path: '/projects' },
  { label: 'Upload', code: 'S02', path: '/upload' },
  { label: 'Datenprüfung', code: 'S04', path: '/data-review/extraction' },
  { label: 'Annahmen', code: 'S05', path: '/assumptions' },
  { label: 'Bewertungsläufe', code: 'S06', path: '/runs' },
  { label: 'Ergebnisse', code: 'S07', path: '/results' },
  { label: 'Dashboards', code: 'S08', path: '/dashboards' },
  { label: 'Berichte', code: 'S18', path: '/reports' },
  { label: 'Admin', code: 'S11', path: '/admin' },
]

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">C</div>
        <div className="sidebar-logo-text">
          <div className="sidebar-logo-title">DCF Workbench</div>
          <div className="sidebar-logo-sub">BOREK × COLLIERS</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-link${isActive ? ' active' : ''}`
            }
          >
            <span>{item.label}</span>
            <span className="sidebar-link-code">{item.code}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-text">Accelerating success</div>
        <div className="sidebar-footer-lines">
          <span /><span /><span /><span /><span />
        </div>
      </div>
    </aside>
  )
}