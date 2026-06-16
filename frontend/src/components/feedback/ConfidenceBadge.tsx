export function ConfidenceBadge({ score }: { score: number }) {
  return (
    <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">
      {Math.round(score * 100)}% confidence
    </span>
  )
}
