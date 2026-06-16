import type { ReactNode } from 'react'
import { Link, Outlet } from 'react-router-dom'

import { Sidebar } from '../components/layout/Sidebar'
import { TopBar } from '../components/layout/TopBar'

type AppLayoutProps = {
  children?: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <TopBar />
        <main className="flex-1 p-6">{children ?? <Outlet />}</main>
      </div>
    </div>
  )
}

export function PlaceholderPage({ title, description }: { title: string; description?: string }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
      {description && <p className="mt-2 text-slate-600">{description}</p>}
      <p className="mt-4 text-sm text-slate-500">
        <Link to="/projects" className="text-blue-600 hover:underline">
          Back to projects
        </Link>
      </p>
    </section>
  )
}
