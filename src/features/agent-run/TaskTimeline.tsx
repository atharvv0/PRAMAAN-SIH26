import { useState } from 'react'
import type { AgentStep } from '@/types/agent'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { cn, formatClock, formatDuration } from '@/lib/utils'
import { ChevronDown, ChevronRight } from 'lucide-react'

export function TaskTimeline({
  steps,
  currentStepId,
  selectedId,
  onSelect,
}: {
  steps: AgentStep[]
  currentStepId?: string
  selectedId?: string
  onSelect: (step: AgentStep) => void
}) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  return (
    <ol className="relative pl-0">
      {steps.map((step, idx) => {
        const isCurrent = step.id === currentStepId
        const isSelected = step.id === selectedId
        const isOpen = expanded[step.id] ?? isCurrent
        const isLast = idx === steps.length - 1

        return (
          <li key={step.id} className="relative flex gap-3">
            <div className="flex flex-col items-center w-4 shrink-0">
              <span
                className={cn(
                  'size-2.5 rounded-full border mt-2 z-[1]',
                  isCurrent
                    ? 'bg-running border-running'
                    : step.status === 'completed' || step.status === 'success'
                      ? 'bg-success border-success'
                      : step.status === 'approval_required'
                        ? 'bg-warning border-warning'
                        : step.status === 'failed' || step.status === 'blocked'
                          ? 'bg-danger border-danger'
                          : 'bg-raised border-border-strong',
                )}
              />
              {!isLast ? (
                <span className="w-px flex-1 bg-border my-0.5" aria-hidden />
              ) : null}
            </div>

            <div
              className={cn(
                'flex-1 min-w-0 border-b border-border/80 pb-2 mb-1',
                isSelected && 'bg-raised/50 -mx-1 px-1 rounded-[2px]',
              )}
            >
              <button
                type="button"
                className="w-full text-left flex items-start gap-1.5 py-1"
                onClick={() => {
                  onSelect(step)
                  setExpanded((e) => ({ ...e, [step.id]: !isOpen }))
                }}
              >
                {isOpen ? (
                  <ChevronDown className="size-3.5 text-text-muted mt-0.5 shrink-0" />
                ) : (
                  <ChevronRight className="size-3.5 text-text-muted mt-0.5 shrink-0" />
                )}
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[12px] font-semibold tracking-wide text-text">
                      {step.label}
                    </span>
                    <StatusBadge status={step.status} compact />
                    {isCurrent ? (
                      <span className="text-[10px] text-running font-medium">LIVE</span>
                    ) : null}
                  </div>
                  <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-0.5 text-[10px] font-mono text-text-muted">
                    {step.startedAt ? <span>{formatClock(step.startedAt)}</span> : null}
                    {step.durationMs != null ? (
                      <span>{formatDuration(step.durationMs)}</span>
                    ) : null}
                    {step.evidenceCount != null ? (
                      <span>ev×{step.evidenceCount}</span>
                    ) : null}
                  </div>
                </div>
              </button>

              {isOpen ? (
                <div className="pl-5 pb-1 space-y-1 text-[11px] text-text-secondary">
                  {step.details ? (
                    <p className="leading-relaxed">{step.details}</p>
                  ) : null}
                  <div className="flex flex-wrap gap-x-3 gap-y-1 text-text-muted font-mono text-[10px]">
                    {step.modelId ? <span>model:{step.modelId}</span> : null}
                    {step.toolId ? <span>tool:{step.toolId}</span> : null}
                  </div>
                  {step.warning ? (
                    <p className="text-warning">{step.warning}</p>
                  ) : null}
                  {step.error ? <p className="text-danger">{step.error}</p> : null}
                </div>
              ) : null}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
