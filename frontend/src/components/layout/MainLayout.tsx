import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopHeader } from './TopHeader'

export type LayoutContext = {
  breadcrumbs: { label: string; current?: boolean }[]
}

export function MainLayout() {
  return (
    <div className="app-shell">
      <div className="app-brand-gradient" aria-hidden="true" />
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
  searchValue,
  onSearchChange,
}: {
  breadcrumbs: { label: string; current?: boolean }[]
  children: React.ReactNode
  searchValue?: string
  onSearchChange?: (value: string) => void
}) {
  return (
    <>
      <TopHeader
        breadcrumbs={breadcrumbs}
        searchValue={searchValue}
        onSearchChange={onSearchChange}
      />
      <div className="page-content">{children}</div>
    </>
  )
}
