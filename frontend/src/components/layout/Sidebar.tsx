import { NavLink } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

import { APP_NAME } from '../../lib/constants'

const navItems = [
  { label: 'Projekte', code: 'S01', path: '/projects' },
  { label: 'Upload', code: 'S02', path: '/upload' },
  { label: 'Datenprüfung', code: 'S04', path: '/data-review/extraction' },
  { label: 'Annahmen', code: 'S05', path: '/assumptions' },
  { label: 'Bewertungsläufe', code: 'S06', path: '/runs' },
  { label: 'Ergebnisse', code: 'S07', path: '/results' },
  { label: 'Dashboards', code: 'S08', path: '/dashboards' },
  { label: 'Berichte', code: 'S18', path: '/reports' },
  { label: 'Admin', code: 'S11', path: '/admin', adminOnly: true },
]

export function Sidebar() {
  const { user } = useAuth()

  const visibleItems = navItems.filter(
    (item) => !item.adminOnly || user?.role === 'admin',
  )

  return (
    <aside className="w-56 border-r border-slate-200 bg-white p-4">
      <div className="mb-6">
        <div className="flex items-center mb-2">
          <div className="sidebar-logo-icon bg-slate-900 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-2">
            C
          </div>
          <div className="sidebar-logo-text">
            <div className="sidebar-logo-title text-base font-bold leading-tight">{APP_NAME}</div>
            <div className="sidebar-logo-sub text-xs text-slate-500">BOREK × COLLIERS</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex justify-between items-center rounded px-3 py-2 text-sm transition-colors ${
                isActive
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            <span>{item.label}</span>
            <span className="sidebar-link-code text-xs font-mono opacity-80">{item.code}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer mt-10">
        <div className="sidebar-footer-text text-xs text-slate-400 mb-2">
          Accelerating success
        </div>
        <div className="sidebar-footer-lines flex gap-1">
          <span className="block w-2 h-0.5 bg-slate-300 rounded" />
          <span className="block w-2 h-0.5 bg-slate-300 rounded" />
          <span className="block w-2 h-0.5 bg-slate-300 rounded" />
          <span className="block w-2 h-0.5 bg-slate-300 rounded" />
          <span className="block w-2 h-0.5 bg-slate-300 rounded" />
        </div>
      </div>
  
    </aside>
  )
}
