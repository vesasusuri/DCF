export function Breadcrumb({ items }: { items: string[] }) {
  return <p className="text-sm text-slate-500">{items.join(' / ')}</p>
}
