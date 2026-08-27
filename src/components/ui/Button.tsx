import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'warning'
type Size = 'sm' | 'md' | 'lg'

const variants: Record<Variant, string> = {
  primary:
    'bg-accent text-canvas hover:brightness-110 border border-accent font-semibold',
  secondary:
    'bg-raised text-text border border-border hover:border-border-strong hover:bg-hover',
  ghost:
    'bg-transparent text-text-secondary hover:text-text hover:bg-raised border border-transparent',
  danger: 'bg-danger-soft text-danger border border-danger/40 hover:bg-danger/20',
  warning: 'bg-warning-soft text-warning border border-warning/40 hover:bg-warning/20',
}

const sizes: Record<Size, string> = {
  sm: 'h-7 px-2.5 text-[11px] gap-1.5',
  md: 'h-8 px-3 text-[12.5px] gap-1.5',
  lg: 'h-9 px-4 text-[13px] gap-2',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export function Button({
  className,
  variant = 'secondary',
  size = 'md',
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-[2px] transition-colors disabled:opacity-40 disabled:pointer-events-none whitespace-nowrap',
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={disabled}
      {...props}
    >
      {leftIcon}
      {children}
      {rightIcon}
    </button>
  )
}
