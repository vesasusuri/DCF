import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, ChevronDown, LogOut } from 'lucide-react'
import { getUserInitials, useAuth } from '../../contexts/AuthContext'

type TopHeaderProps = {
  breadcrumbs: { label: string; current?: boolean }[]
}

export function TopHeader({ breadcrumbs }: TopHeaderProps) {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const initials = user ? getUserInitials(user.fullName) : 'U'

  async function handleSignOut() {
    await signOut()
    navigate('/login', { replace: true })
  }

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

        <div className="user-menu">
          <button
            type="button"
            className="user-avatar"
            title={user?.email ?? 'Benutzer'}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {initials}
          </button>

          {menuOpen && (
            <div className="user-menu-dropdown card">
              <div className="user-menu-name">{user?.fullName}</div>
              <div className="user-menu-email">{user?.email}</div>
              <div className="user-menu-role">
                <span className={`badge ${user?.role === 'admin' ? 'badge-warning' : 'badge-neutral'}`}>
                  {user?.role === 'admin' ? 'Admin' : 'Benutzer'}
                </span>
              </div>
              <button type="button" className="user-menu-logout" onClick={() => void handleSignOut()}>
                <LogOut size={14} />
                Abmelden
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
