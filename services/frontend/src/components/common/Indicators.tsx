import { Activity, ShieldCheck } from 'lucide-react'
import { useHealth, useSovereignty } from '@/hooks'
import { cn } from '@/lib/utils'

export function SovereigntyIndicator({ active = true, compact = false, className }: { active?: boolean; compact?: boolean; className?: string }) {
  return (
    <span aria-live="polite" className={cn('inline-flex items-center gap-1.5 border px-2 py-1', active ? 'border-accent/40 bg-accent-soft text-accent' : 'border-border bg-raised text-text-muted', className)}>
      <span className={cn('size-1.5 rounded-full', active ? 'bg-accent' : 'bg-text-muted')} aria-hidden />
      <ShieldCheck className={compact ? 'size-3' : 'size-3.5'} aria-hidden />
      <span className={cn('font-semibold tracking-wide', compact ? 'text-[10px]' : 'text-[11px]')}>{compact ? 'SOVEREIGN' : 'SOVEREIGN MODE'}</span>
      {!compact ? <span className="border-l border-border pl-1.5 text-[10px] text-text-muted">{active ? 'ACTIVE' : 'OFF'}</span> : null}
    </span>
  )
}

export function ModelBadge({ name, local = true }: { name: string; local?: boolean }) {
  return (
    <span className="inline-flex items-center gap-1.5 border border-border bg-raised px-2 py-1 text-[11px] text-text">
      <span className={cn('size-1.5 rounded-full', local ? 'bg-success' : 'bg-warning')} aria-hidden />
      <span className="font-medium">{name}</span>
      <span className="text-text-muted">{local ? 'local' : 'deterministic'}</span>
    </span>
  )
}

export function HealthIndicator({ compact = false }: { compact?: boolean }) {
  const health = useHealth()
  const healthy = health.isSuccess && health.data?.status !== 'offline'
  const label = health.isLoading ? 'CHECKING' : healthy ? 'LOCAL API' : 'API OFFLINE'
  return (
    <span className={cn('inline-flex items-center gap-1.5 border px-2 py-1 text-[10px] font-semibold tracking-wide', healthy ? 'border-success/35 bg-success-soft text-success' : 'border-danger/35 bg-danger-soft text-danger', compact && 'px-1.5')} title={healthy ? 'Local PRAMAAN API is reachable' : 'The local PRAMAAN API cannot be reached'}>
      <Activity className={cn('size-3', health.isLoading && 'animate-pulse')} aria-hidden />
      {label}
    </span>
  )
}

export function LiveSovereigntyIndicator() {
  const { data } = useSovereignty()
  return <SovereigntyIndicator active={data?.mode === 'active'} compact />
}
