import { ShieldCheck } from 'lucide-react'
import { cn } from '@/lib/utils'

export function SovereigntyIndicator({
  active = true,
  compact = false,
  className,
}: {
  active?: boolean
  compact?: boolean
  className?: string
}) {
  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 border',
        active
          ? 'border-accent/45 bg-accent-soft text-accent'
          : 'border-border bg-raised text-text-muted',
        compact ? 'px-1.5 py-0.5' : 'px-2 py-1',
        className,
      )}
      title={
        active
          ? 'Sovereign Mode ACTIVE — egress deny-by-default'
          : 'Sovereign Mode inactive'
      }
    >
      <span
        className={cn(
          'size-1.5 rounded-full',
          active ? 'bg-accent' : 'bg-text-muted',
        )}
        aria-hidden
      />
      <ShieldCheck className={cn(compact ? 'size-3' : 'size-3.5')} aria-hidden />
      <span className={cn('font-semibold', compact ? 'text-[10px]' : 'text-[11px]')}>
        {compact ? 'SOVEREIGN' : 'SOVEREIGN MODE'}
      </span>
      {!compact ? (
        <span className="text-[10px] text-text-muted border-l border-border pl-1.5">
          {active ? 'ACTIVE' : 'OFF'}
        </span>
      ) : null}
    </div>
  )
}

export function ModelBadge({
  name,
  local = true,
}: {
  name: string
  local?: boolean
}) {
  return (
    <span
      className="inline-flex items-center gap-1.5 border border-border bg-raised px-2 py-0.5 text-[11px] text-text"
      title={local ? 'Local runtime' : 'Non-local runtime'}
    >
      <span
        className={cn('size-1.5 rounded-full', local ? 'bg-success' : 'bg-warning')}
        aria-hidden
      />
      <span className="font-medium">{name}</span>
      {local ? <span className="text-text-muted">local</span> : null}
    </span>
  )
}
