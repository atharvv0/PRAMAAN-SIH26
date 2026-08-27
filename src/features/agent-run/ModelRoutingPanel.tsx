import type { ModelRouting } from '@/types/agent'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { ModelBadge } from '@/components/common/Indicators'
import { EmptyState, SectionLabel } from '@/components/common/States'

export function ModelRoutingPanel({ routings }: { routings: ModelRouting[] }) {
  return (
    <section className="border border-border bg-panel flex flex-col min-h-0 h-full">
      <SectionLabel>Model routing</SectionLabel>
      {routings.length === 0 ? (
        <EmptyState
          title="No routings yet"
          description="Local adapters will appear as the plan advances."
          className="m-3 border-0"
        />
      ) : (
        <ul className="overflow-y-auto divide-y divide-border flex-1">
          {routings.map((r) => (
            <li key={`${r.stepId}-${r.modelId}`} className="px-3 py-2.5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-[12px] font-medium text-text">{r.taskLabel}</span>
                <StatusBadge status={r.status} compact />
              </div>
              <div className="mt-1.5">
                <ModelBadge name={r.modelName} local={r.local} />
              </div>
              <p className="mt-1.5 text-[11px] text-text-secondary leading-relaxed">
                {r.reason}
              </p>
              <div className="mt-1 font-mono text-[10px] text-text-muted">{r.modelId}</div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
