import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
}

export function Button({ children, loading, disabled, ...props }: ButtonProps) {
  let content = children

  if (loading) {
    content = 'Please wait...'
  }

  return (
    <button className="button" disabled={disabled || loading} {...props}>
      {content}
    </button>
  )
}
