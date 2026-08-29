import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { DataTable, Td } from '@/components/common/DataTable'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  MetaRow,
  PageHeader,
  SectionLabel,
} from '@/components/common/States'
import { SovereigntyIndicator } from '@/components/common/Indicators'
import { useOverview } from '@/hooks'
import { formatClock, formatDateTime } from '@/lib/utils'

export function OverviewPage() {
  const { data, isLoading, isError, refetch } = useOverview()

  if (isLoading) return <LoadingState label="Loading operational overview…" />
  if (isError || !data) {
    return (
      <ErrorState
        title="Overview unavailable"
        description="Could not load dashboard state from the local API."
        onRetry={() => void refetch()}
      />
    )
  }

  const sov = data.sovereignty

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Operations"
        title="Overview"
        description="Live workbench status for sovereign inspection review."
        actions={
          <Link
            to="/tasks/new"
            className="h-7 inline-flex items-center px-2.5 text-[11px] font-semibold bg-accent text-canvas hover:brightness-110"
          >
            New task
          </Link>
        }
      />

      {/* KPI strip as instrument readout */}
      <div className="border border-border bg-panel grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
        <KpiCell
          label="Sovereign"
          value={
            <span className="inline-flex items-center gap-2">
              <SovereigntyIndicator compact />
            </span>
          }
        />
        <KpiCell
          label="Egress"
          value={
            <span className="text-blocked text-[11px] font-semibold tracking-wide">
              {sov.egressPolicy === 'deny_by_default' ? 'DENY DEFAULT' : 'ALLOWLIST'}
            </span>
          }
        />
        <KpiCell
          label="Local models"
          value={
            <span className="font-mono tabular text-[13px]">
              {sov.healthyModels}
              <span className="text-text-muted">/{sov.totalModels}</span>
            </span>
          }
        />
        <KpiCell
          label="Active tasks"
          value={<span className="font-mono tabular text-[15px]">{data.activeTasks}</span>}
        />
        <KpiCell
          label="Approvals"
          value={
            <span className="font-mono tabular text-[15px] text-warning">
              {data.pendingApprovals}
            </span>
          }
        />
        <KpiCell
          label="Blocked egress"
          value={
            <span className="font-mono tabular text-[15px] text-blocked">
              {sov.externalBlocked}
            </span>
          }
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_300px] gap-3">
        <section className="border border-border bg-panel min-w-0 flex flex-col">
          <SectionLabel right={<span className="text-text-muted">{data.currentTasks.length} open</span>}>
            Current tasks
          </SectionLabel>
          {data.currentTasks.length === 0 ? (
            <EmptyState
              title="No active tasks"
              description="Create a work package to begin local agent execution."
              className="m-3"
              action={
                <Link to="/tasks/new" className="text-[11px] text-accent hover:underline mt-1">
                  New task →
                </Link>
              }
            />
          ) : (
            <DataTable
              columns={['Task', 'Workspace', 'Status', 'Progress', 'Step', 'Updated']}
              className="border-0"
            >
              {data.currentTasks.map((task) => (
                <tr key={task.id} className="hover:bg-raised/50">
                  <Td>
                    <Link
                      to={task.runId ? `/runs/${task.runId}` : '/tasks'}
                      className="text-text hover:text-accent font-medium"
                    >
                      {task.title}
                    </Link>
                  </Td>
                  <Td>{task.workspaceName}</Td>
                  <Td>
                    <StatusBadge status={task.status} compact />
                  </Td>
                  <Td mono>
                    <div className="flex items-center gap-2 min-w-[72px]">
                      <div className="flex-1 h-1 bg-canvas border border-border overflow-hidden">
                        <div
                          className="h-full bg-running"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span>{task.progress}%</span>
                    </div>
                  </Td>
                  <Td>
                    <span className="text-[10px] text-text-muted uppercase tracking-wide">
                      {task.currentStep ?? '—'}
                    </span>
                  </Td>
                  <Td mono>{formatClock(task.updatedAt)}</Td>
                </tr>
              ))}
            </DataTable>
          )}
        </section>

        <aside className="space-y-3 min-w-0">
          <section className="border border-border bg-panel">
            <SectionLabel>Sovereignty</SectionLabel>
            <dl className="px-3 py-1.5">
              <MetaRow label="Enforcement" value={<span className="text-success font-semibold">ENFORCED</span>} />
              <MetaRow
                label="Network"
                value={
                  sov.egressPolicy === 'deny_by_default'
                    ? 'Deny-by-default'
                    : 'Allowlist'
                }
              />
              <MetaRow
                label="Allowed"
                value={<span className="font-mono">{sov.externalAllowed}</span>}
                mono
              />
              <MetaRow
                label="Blocked"
                value={
                  <span className="font-mono text-blocked">{sov.externalBlocked}</span>
                }
              />
              <MetaRow
                label="Local"
                value={
                  <span className="font-mono">{sov.localProcessingPercent}%</span>
                }
              />
              <MetaRow
                label="Audit"
                value={sov.auditRecording ? 'Recording' : 'Off'}
              />
            </dl>
            <div className="border-t border-border px-3 py-2">
              <Link to="/sovereignty" className="text-[11px] text-accent hover:underline">
                Open sovereignty console →
              </Link>
            </div>
          </section>

          <section className="border border-border bg-panel">
            <SectionLabel>Activity</SectionLabel>
            <ul className="max-h-[260px] overflow-y-auto divide-y divide-border">
              {data.activity.slice(0, 8).map((ev) => (
                <li key={ev.id} className="px-3 py-2 text-[12px]">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[10px] text-text-muted">
                      {formatClock(ev.timestamp)}
                    </span>
                    <StatusBadge status={ev.status} compact showIcon={false} />
                  </div>
                  <div className="text-text mt-0.5 font-medium leading-snug">{ev.action}</div>
                  <div className="text-text-muted text-[11px] leading-snug mt-0.5 line-clamp-2">
                    {ev.result}
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </aside>
      </div>

      <section className="border border-border bg-panel">
        <SectionLabel right={<Link to="/sovereignty" className="text-accent hover:underline normal-case tracking-normal text-[10px]">Full timeline</Link>}>
          Network events
        </SectionLabel>
        {data.networkEvents.length === 0 ? (
          <EmptyState title="No network events" className="m-3 border-0" />
        ) : (
          <ul className="divide-y divide-border">
            {data.networkEvents.slice(0, 5).map((ev) => (
              <li
                key={ev.id}
                className="px-3 py-2 flex flex-wrap items-start gap-x-4 gap-y-1 text-[12px]"
              >
                <span className="font-mono text-[11px] text-text-muted w-[68px] shrink-0">
                  {formatClock(ev.timestamp)}
                </span>
                <span className="text-micro text-text-secondary w-[110px] shrink-0">
                  {ev.kind.replace(/_/g, ' ')}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="text-text-secondary">{ev.message}</div>
                  {ev.destination ? (
                    <div className="font-mono text-[10px] text-text-muted mt-0.5 truncate">
                      {ev.destination}
                    </div>
                  ) : null}
                </div>
                {ev.decision ? (
                  <span
                    className={
                      ev.decision === 'blocked'
                        ? 'text-blocked text-[11px] font-semibold'
                        : 'text-success text-[11px] font-semibold'
                    }
                  >
                    {ev.decision.toUpperCase()}
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        <div className="border-t border-border px-3 py-1.5 text-[10px] text-text-muted font-mono">
          {formatDateTime(new Date().toISOString())} · security events {data.recentSecurityEvents}
        </div>
      </section>
    </div>
  )
}

function KpiCell({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="min-w-0 px-3 py-2.5 border-b xl:border-b-0 border-r border-border last:border-r-0 odd:border-r md:[&:nth-child(3n)]:border-r-0 xl:[&:nth-child(3n)]:border-r">
      <div className="text-micro text-text-muted mb-1">{label}</div>
      <div className="text-text min-h-[22px] flex items-center">{value}</div>
    </div>
  )
}
