import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode
  variant?: 'primary' | 'secondary'
}

export function Button({ children, variant = 'primary', className = '', ...props }: ButtonProps) {
  const styles =
    variant === 'primary'
      ? 'bg-slate-900 text-white hover:bg-slate-800'
      : 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50'

  return (
    <button
      className={`rounded px-4 py-2 text-sm font-medium transition ${styles} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
