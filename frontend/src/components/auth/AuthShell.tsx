import type { ReactNode } from 'react'

type AuthShellProps = {
  eyebrow: string
  title: string
  subtitle?: string
  children: ReactNode
}

export function AuthShell({ eyebrow, title, subtitle, children }: AuthShellProps) {
  return (
    <div className="login-shell">
      <div className="app-brand-gradient" aria-hidden="true" />

      <div className="login-page">
        <div className="login-card card">
          <div className="login-card-gradient" aria-hidden="true" />

          <div className="login-brand">
            <div className="login-logo-icon">C</div>
            <div>
              <div className="login-logo-title">DCF Workbench</div>
              <div className="login-logo-sub">BOREK × COLLIERS</div>
            </div>
          </div>

          <div className="login-header">
            <div className="page-eyebrow login-eyebrow">{eyebrow}</div>
            <h1 className="page-title login-title">{title}</h1>
            {subtitle && <p className="login-subtitle">{subtitle}</p>}
          </div>

          {children}
        </div>
      </div>
    </div>
  )
}
