import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopHeader } from './TopHeader'

export type LayoutContext = {
  breadcrumbs: { label: string; current?: boolean }[]
}

export function MainLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <Outlet />
      </div>
    </div>
  )
}

export function PageWrapper({
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
