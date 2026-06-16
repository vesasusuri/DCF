import { Outlet } from 'react-router-dom'
import { AdminSidebar } from './AdminSidebar'
import { TopHeader } from './TopHeader'

export function AdminLayout() {
  return (
    <div className="app-shell">
      <div className="app-brand-gradient" aria-hidden="true" />
      <AdminSidebar />
      <div className="main-area">
        <Outlet />
      </div>
    </div>
  )
}

export function AdminPageWrapper({
  breadcrumbs,
  children,
}: {
  breadcrumbs: { label: string; current?: boolean }[]
  children: React.ReactNode
}) {
  return (
    <>
      <TopHeader breadcrumbs={breadcrumbs} />
      <div className="page-content">{children}</div>
    </>
  )
}
