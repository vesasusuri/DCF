import type { ReactNode } from 'react'

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      {title && <h3 className="mb-2 text-sm font-semibold text-slate-900">{title}</h3>}
      {children}
    </div>
  )
}
