import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, Check, Clock3 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Field'
import { StatusBadge } from '@/components/ui/StatusBadge'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  SectionLabel,
} from '@/components/common/States'
import { useApprovals, useDecideApproval } from '@/hooks'
import { useAuthStore } from '@/store'
import { formatDateTime } from '@/lib/utils'
import type { ApprovalStatus } from '@/types/deliverable'

export function ApprovalsPage() {
  const query = useApprovals()
  const decide = useDecideApproval()
  const user = useAuthStore((state) => state.user)
  const [error, setError] = useState<string | null>(null)
  const [notes, setNotes] = useState<Record<string, string>>({})

  async function onDecide(
    deliverableId: string,
    decision: Exclude<ApprovalStatus, 'pending'>,
  ) {
    setError(null)

    try {
      await decide.mutateAsync({
        deliverableId,
        decision,
        actor: user?.id ?? 'local-session',
        note: notes[deliverableId]?.trim() || undefined,
      })
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Approval decision failed.')
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="Human control"
        title="Approvals"
        description="Explicit review gates before a deliverable can be treated as approved."
      />

      <div className="border border-warning/35 bg-warning-soft px-4 py-3 text-[11.5px] leading-relaxed text-warning">
        <div className="flex items-center gap-2 font-semibold">
          <AlertTriangle className="size-4" aria-hidden="true" />
          Human decision required
        </div>
        <p className="mt-1">
          PRAMAAN will not represent an approval outcome until the backend confirms the decision.
        </p>
      </div>

      {error ? (
        <ErrorState className="m-0" title="Decision failed" description={error} />
      ) : null}

      {query.isLoading ? <LoadingState label="Loading approval queue…" /> : null}

      {query.isError ? (
        <ErrorState
          title="Approvals unavailable"
          description="The local API could not return approval state."
          onRetry={() => void query.refetch()}
        />
      ) : null}

      {!query.isLoading && !query.isError && query.data?.length === 0 ? (
        <EmptyState
          title="No approvals waiting"
          description="The backend reports no deliverables currently awaiting a human decision."
        />
      ) : null}

      {!query.isLoading && !query.isError
        ? query.data?.map((item) => (
            <section key={item.id} className="border border-border bg-panel">
              <SectionLabel right={<span className="font-mono text-[10px]">{item.id}</span>}>
                {item.name}
              </SectionLabel>

              <div className="grid gap-4 p-4 lg:grid-cols-[minmax(0,1fr)_300px]">
                <div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={item.status} />
                    <span className="text-[11px] text-text-muted">
                      Approval: {item.approvalStatus.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <h2 className="mt-3 text-[14px] font-semibold text-text">{item.taskTitle}</h2>

                  <p className="mt-2 max-w-3xl text-[12px] leading-relaxed text-text-secondary">
                    {item.provenanceSummary ||
                      'No provenance summary was returned by the backend.'}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <Link
                      to={`/evidence?taskId=${encodeURIComponent(item.taskId)}`}
                      className="inline-flex h-7 items-center border border-border bg-raised px-2.5 text-[11px] font-medium text-text hover:bg-hover"
                    >
                      Review evidence
                    </Link>
                    <Link
                      to={`/audit?taskId=${encodeURIComponent(item.taskId)}`}
                      className="inline-flex h-7 items-center border border-border bg-raised px-2.5 text-[11px] font-medium text-text hover:bg-hover"
                    >
                      Open audit
                    </Link>
                  </div>
                </div>

                <div className="border border-border bg-surface">
                  <div className="grid grid-cols-2 gap-px bg-border">
                    <Stat
                      icon={<Clock3 aria-hidden="true" />}
                      label="Created"
                      value={formatDateTime(item.createdAt)}
                    />
                    <Stat
                      icon={<Check aria-hidden="true" />}
                      label="Evidence"
                      value={String(item.evidenceCount)}
                    />
                  </div>

                  <div className="border-t border-border p-3">
                    <div className="text-micro text-text-muted">Decision</div>

                    <div className="mt-2 space-y-2">
                      <Textarea
                        value={notes[item.id] ?? ''}
                        onChange={(event) =>
                          setNotes((current) => ({
                            ...current,
                            [item.id]: event.target.value,
                          }))
                        }
                        placeholder="Optional decision note"
                        className="min-h-[78px]"
                      />

                      <div className="grid gap-2">
                        <Button
                          variant="primary"
                          disabled={decide.isPending}
                          onClick={() => void onDecide(item.id, 'approved')}
                        >
                          Approve
                        </Button>
                        <Button
                          variant="warning"
                          disabled={decide.isPending}
                          onClick={() => void onDecide(item.id, 'changes_requested')}
                        >
                          Request changes
                        </Button>
                        <Button
                          variant="danger"
                          disabled={decide.isPending}
                          onClick={() => void onDecide(item.id, 'rejected')}
                        >
                          Reject
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          ))
        : null}
    </div>
  )
}

function Stat({
  icon,
  label,
  value,
}: {
  icon: ReactNode
  label: string
  value: string
}) {
  return (
    <div className="bg-surface p-3">
      <div className="flex items-center gap-1.5 text-text-muted">
        <span className="text-accent">{icon}</span>
        <span className="text-micro">{label}</span>
      </div>
      <div className="mt-1.5 text-[11px] text-text">{value}</div>
    </div>
  )
}
