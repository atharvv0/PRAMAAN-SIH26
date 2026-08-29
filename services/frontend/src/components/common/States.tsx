import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, ArrowLeft, Ban, FileQuestion, Loader2, RefreshCw, WifiOff } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'

export function LoadingState({ label = 'Loading…', className }: { label?: string; className?: string }) {
  return <div className={cn('flex items-center gap-2 border border-border bg-panel px-4 py-8 text-[12.5px] text-text-secondary', className)} role="status"><Loader2 className="size-4 animate-spin text-accent" aria-hidden />{label}</div>
}

export function EmptyState({ title, description, action, className }: { title: string; description?: string; action?: ReactNode; className?: string }) {
  return <div className={cn('border border-dashed border-border bg-surface/60 px-4 py-8', className)}><div className="flex items-center gap-2"><FileQuestion className="size-4 text-text-muted" aria-hidden /><p className="text-[13px] font-semibold text-text">{title}</p></div>{description ? <p className="mt-1.5 max-w-xl text-[11.5px] leading-relaxed text-text-muted">{description}</p> : null}{action ? <div className="mt-3">{action}</div> : null}</div>
}

export function ErrorState({ title = 'Unable to load data', description, onRetry, className }: { title?: string; description?: string; onRetry?: () => void; className?: string }) {
  return <div className={cn('border border-danger/35 bg-danger-soft px-4 py-5', className)} role="alert"><div className="flex items-center gap-2 text-danger"><AlertTriangle className="size-4" aria-hidden /><p className="text-[13px] font-semibold">{title}</p></div>{description ? <p className="mt-1.5 max-w-2xl text-[11.5px] leading-relaxed text-text-secondary">{description}</p> : null}{onRetry ? <Button size="sm" className="mt-3" onClick={onRetry} leftIcon={<RefreshCw className="size-3.5" />}>Retry</Button> : null}</div>
}

export function BackendUnavailableState({ onRetry }: { onRetry: () => void }) {
  return <div className="border border-warning/40 bg-warning-soft px-4 py-5" role="alert"><div className="flex items-center gap-2 text-warning"><WifiOff className="size-4" aria-hidden /><p className="text-[13px] font-semibold">Local API unavailable</p></div><p className="mt-1.5 max-w-2xl text-[11.5px] leading-relaxed text-text-secondary">PRAMAAN could not reach the configured local backend. No synthetic or cached system state is being shown.</p><Button size="sm" className="mt-3" onClick={onRetry} leftIcon={<RefreshCw className="size-3.5" />}>Retry</Button></div>
}

export function BlockedState({ title = 'Action blocked by Sovereignty Policy', description, className }: { title?: string; description?: string; className?: string }) {
  return <div className={cn('flex items-start gap-2 border border-blocked/35 bg-blocked-soft px-4 py-5', className)} role="status"><Ban className="mt-0.5 size-4 shrink-0 text-blocked" aria-hidden /><div><p className="text-[13px] font-semibold text-blocked">{title}</p>{description ? <p className="mt-1 text-[11.5px] leading-relaxed text-text-secondary">{description}</p> : null}</div></div>
}

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description?: string; actions?: ReactNode }) {
  return <header className="flex flex-col gap-3 border-b border-border pb-4 md:flex-row md:items-end md:justify-between"><div className="min-w-0 border-l-2 border-accent pl-3"><div className="flex items-center gap-2">{eyebrow ? <p className="text-micro text-accent">{eyebrow}</p> : null}</div><h1 className="mt-1 text-xl font-semibold tracking-tight text-text">{title}</h1>{description ? <p className="mt-1.5 max-w-3xl text-[12px] leading-relaxed text-text-muted">{description}</p> : null}</div>{actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}</header>
}

export function SectionLabel({ children, right }: { children: ReactNode; right?: ReactNode }) { return <div className="panel-header justify-between"><span>{children}</span>{right ? <span className="normal-case tracking-normal font-normal">{right}</span> : null}</div> }

export function MetaRow({ label, value, mono }: { label: string; value: ReactNode; mono?: boolean }) { return <div className="grid grid-cols-[132px_minmax(0,1fr)] gap-3 border-b border-border/70 py-2 last:border-0"><dt className="text-[11px] text-text-muted">{label}</dt><dd className={cn('break-words text-[12px] text-text', mono && 'font-mono text-[11px]')}>{value}</dd></div> }

export function BackLink({ to = '..' }: { to?: string }) {
  return (
    <Link to={to} className="inline-flex items-center gap-1.5 text-[11px] text-text-muted hover:text-accent">
      <ArrowLeft className="size-3.5" aria-hidden />
      Back
    </Link>
  )
}
