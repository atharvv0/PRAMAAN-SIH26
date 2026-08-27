import type { ToolInvocation } from '@/types/agent'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { EmptyState, SectionLabel } from '@/components/common/States'
import { formatClock, formatDuration } from '@/lib/utils'
import { cn } from '@/lib/utils'

export function ToolTracePanel({ invocations }: { invocations: ToolInvocation[] }) {
  return (
    <section className="border border-border bg-panel flex flex-col min-h-0 h-full">
      <SectionLabel>Tool trace</SectionLabel>
      {invocations.length === 0 ? (
        <EmptyState
          title="No tool invocations"
          description="Allowed and blocked tool calls stream here during execution."
          className="m-3 border-0"
        />
      ) : (
        <ul className="overflow-y-auto divide-y divide-border flex-1">
          {invocations.map((inv) => (
            <li key={inv.id} className="px-3 py-2.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-[12px] text-text font-semibold">
                  {inv.tool}
                </span>
                <StatusBadge status={inv.status} compact />
                <span
                  className={cn(
                    'text-[10px] font-semibold uppercase tracking-wide',
                    inv.permission === 'blocked' ? 'text-blocked' : 'text-success',
                  )}
                >
                  {inv.permission}
                </span>
                <span className="ml-auto font-mono text-[10px] text-text-muted">
                  {formatClock(inv.timestamp)}
                  {inv.durationMs != null ? ` · ${formatDuration(inv.durationMs)}` : ''}
                </span>
              </div>
              <p className="mt-1 text-[11px] text-text-secondary leading-relaxed">
                {inv.reason}
              </p>
              {inv.inputSummary ? (
                <div className="mt-1.5 text-[10px] font-mono text-text-muted truncate">
                  IN  {inv.inputSummary}
                </div>
              ) : null}
              {inv.outputSummary ? (
                <div className="text-[10px] font-mono text-text-muted truncate">
                  OUT {inv.outputSummary}
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
