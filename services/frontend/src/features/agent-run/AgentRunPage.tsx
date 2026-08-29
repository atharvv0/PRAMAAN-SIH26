import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { AgentStep } from '@/types/agent'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { ModelBadge } from '@/components/common/Indicators'
import {
  ErrorState,
  LoadingState,
  MetaRow,
  SectionLabel,
} from '@/components/common/States'
import { useAgentRun, useEvidence, useTask, useTaskEvents } from '@/hooks'
import { formatClock, formatDuration } from '@/lib/utils'
import { TaskTimeline } from './TaskTimeline'
import { ModelRoutingPanel } from './ModelRoutingPanel'
import { ToolTracePanel } from './ToolTracePanel'

export function AgentRunPage() {
  const { runId } = useParams<{ runId: string }>()
  const runQuery = useAgentRun(runId)
  const run = runQuery.data
  const taskQuery = useTask(run?.taskId ?? '')
  const evidenceQuery = useEvidence(run?.taskId, runId)
  const eventQuery = useTaskEvents(run?.taskId ?? '')

  const [selectedStep, setSelectedStep] = useState<AgentStep | null>(null)
  const task = taskQuery.data

  useEffect(() => {
    if (!run) return
    setSelectedStep((prev) => {
      if (prev) {
        const refreshed = run.plan.find((s) => s.id === prev.id)
        if (refreshed) return refreshed
      }
      return (
        run.plan.find((s) => s.id === run.currentStepId) ??
        run.plan[run.plan.length - 1] ??
        null
      )
    })
  }, [run])

  const evidenceCount = evidenceQuery.data?.length ?? 0
  const inspector = useMemo(() => selectedStep, [selectedStep])

  if (runQuery.isLoading) {
    return <LoadingState label="Connecting to execution console…" />
  }

  if (runQuery.isError || !run) {
    return (
      <ErrorState
        title="Run not found"
        description={`No agent state for run ${runId ?? '—'}.`}
        onRetry={() => void runQuery.refetch()}
      />
    )
  }

  return (
    <div className="space-y-2 h-full flex flex-col min-h-[620px]">
      {/* Console chrome */}
      <div className="border border-border bg-panel">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 px-3 py-2.5">
          <div className="min-w-0 flex-1 rail pl-3">
            <div className="text-micro text-text-muted">Execution console</div>
            <h1 className="text-[15px] font-semibold text-text truncate leading-tight mt-0.5">
              {task?.title ?? 'Agent run'}
            </h1>
            <div className="font-mono text-[10px] text-text-muted mt-0.5">
              {run.id}
              <span className="text-border-strong mx-1.5">·</span>
              task {run.taskId}
            </div>
          </div>

          <StatusBadge status={run.status} />

          <div className="flex items-center gap-2 min-w-[150px]">
            <div className="flex-1 h-1.5 bg-canvas border border-border overflow-hidden">
              <div
                className="h-full bg-accent transition-[width] duration-300"
                style={{ width: `${run.progress}%` }}
              />
            </div>
            <span className="font-mono text-[11px] text-text tabular w-9 text-right">
              {run.progress}%
            </span>
          </div>

          {task?.model ? <ModelBadge name={task.model} local /> : null}

          <div className="flex items-center gap-3 text-[12px]">
            <Link
              to={`/evidence?runId=${run.id}`}
              className="text-accent hover:underline font-medium"
            >
              Evidence · {evidenceCount}
            </Link>
            {run.status === 'approval_required' ? (
              <Link
                to="/approvals"
                className="text-warning hover:underline font-semibold"
              >
                Approvals →
              </Link>
            ) : null}
          </div>
        </div>

        {task?.instruction ? (
          <div className="border-t border-border px-3 py-2 bg-surface/50">
            <div className="text-micro text-text-muted mb-1">Operator intent</div>
            <p className="text-[11.5px] text-text-secondary leading-relaxed line-clamp-2">
              {task.instruction}
            </p>
          </div>
        ) : null}
      </div>

      {/* Console body */}
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(260px,0.42fr)_minmax(0,1fr)] gap-2 flex-1 min-h-0">
        <section className="border border-border bg-panel flex flex-col min-h-[300px]">
          <SectionLabel
            right={
              <span className="font-mono text-[10px] text-text-muted">
                {run.plan.length} steps
              </span>
            }
          >
            Execution timeline
          </SectionLabel>
          <div className="p-2.5 overflow-y-auto flex-1">
            <TaskTimeline
              steps={run.plan}
              currentStepId={run.currentStepId}
              selectedId={selectedStep?.id}
              onSelect={setSelectedStep}
            />
          </div>
        </section>

        <div className="grid grid-rows-[minmax(240px,1fr)_auto] gap-2 min-h-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 min-h-0">
            <ModelRoutingPanel routings={run.modelRoutings} />
            <ToolTracePanel invocations={run.toolInvocations} />
          </div>

          <section className="border border-border bg-panel">
            <SectionLabel>Step inspector</SectionLabel>
            {inspector ? (
              <div className="px-3 py-2 grid grid-cols-1 md:grid-cols-2 gap-x-6">
                <dl>
                  <MetaRow label="Step" value={inspector.label} />
                  <MetaRow
                    label="Status"
                    value={<StatusBadge status={inspector.status} compact />}
                  />
                  <MetaRow
                    label="Started"
                    value={
                      inspector.startedAt ? formatClock(inspector.startedAt) : '—'
                    }
                    mono
                  />
                  <MetaRow
                    label="Duration"
                    value={formatDuration(inspector.durationMs)}
                    mono
                  />
                </dl>
                <dl>
                  <MetaRow label="Model" value={inspector.modelId ?? '—'} mono />
                  <MetaRow label="Tool" value={inspector.toolId ?? '—'} mono />
                  <MetaRow
                    label="Evidence"
                    value={String(inspector.evidenceCount ?? 0)}
                    mono
                  />
                  <MetaRow
                    label="Updated"
                    value={formatClock(run.updatedAt)}
                    mono
                  />
                </dl>
                {inspector.details ? (
                  <p className="md:col-span-2 text-[12px] text-text-secondary leading-relaxed border-t border-border pt-2 mt-1">
                    {inspector.details}
                  </p>
                ) : null}
                {inspector.warning ? (
                  <p className="md:col-span-2 text-[12px] text-warning">
                    {inspector.warning}
                  </p>
                ) : null}
              </div>
            ) : (
              <p className="px-3 py-4 text-[12px] text-text-muted">
                Select a timeline step to inspect.
              </p>
            )}
          </section>
        </div>
      </div>

      <section className="border border-border bg-panel">
        <SectionLabel right={<span className="font-mono text-[10px]">{eventQuery.data?.length ?? run.events?.length ?? 0}</span>}>Execution events</SectionLabel>
        {eventQuery.isError ? <ErrorState className="m-3" title="Execution events unavailable" onRetry={() => void eventQuery.refetch()} /> : (eventQuery.data?.length ?? run.events?.length ?? 0) === 0 ? <p className="px-4 py-4 text-[11px] text-text-muted">No execution events have been returned for this run.</p> : <ul className="divide-y divide-border">{(eventQuery.data ?? run.events ?? []).slice(0, 12).map((event, index) => <li key={String(event.id ?? `${run.id}-${index}`)} className="grid gap-2 px-4 py-2.5 text-[11px] sm:grid-cols-[90px_minmax(0,1fr)]"><span className="font-mono text-[10px] text-text-muted">{typeof event.timestamp === 'string' ? formatClock(event.timestamp) : '—'}</span><span className="text-text-secondary">{typeof event.message === 'string' ? event.message : typeof event.action === 'string' ? event.action : JSON.stringify(event)}</span></li>)}</ul>}
      </section>
    </div>
  )
}
