import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Settings,
  Activity,
  Shield,
} from 'lucide-react'

const adminNavItems = [
  { label: 'Übersicht', code: 'A01', path: '/admin', icon: LayoutDashboard, end: true },
  { label: 'Benutzer', code: 'A02', path: '/admin/users', icon: Users },
  { label: 'Einstellungen', code: 'A03', path: '/admin/settings', icon: Settings },
  { label: 'Audit', code: 'A04', path: '/admin/audit', icon: Activity },
  { label: 'Sicherheit', code: 'A05', path: '/admin/security', icon: Shield },
]

export function AdminSidebar() {
  return (
    <aside className="sidebar admin-sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon admin-sidebar-logo">A</div>
        <div className="sidebar-logo-text">
          <div className="sidebar-logo-title">Admin Console</div>
          <div className="sidebar-logo-sub">DCF WORKBENCH</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {adminNavItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `sidebar-link${isActive ? ' active' : ''}`
              }
            >
              <span className="sidebar-link-label">
                <Icon size={15} />
                <span>{item.label}</span>
              </span>
              <span className="sidebar-link-code">{item.code}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-text">System administration</div>
        <div className="sidebar-footer-lines">
          <span /><span /><span /><span /><span />
        </div>
      </div>
    </aside>
  )
}
