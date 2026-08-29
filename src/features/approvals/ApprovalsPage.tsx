import { Link } from "react-router-dom";
import { AlertTriangle } from "lucide-react";

import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  SectionLabel,
} from "@/components/common/States";
import { useApprovals, useDecideApproval } from "@/hooks";
import { useAuthStore } from "@/store";
import { formatDateTime } from "@/lib/utils";
import type { ApprovalStatus } from "@/types/deliverable";

export function ApprovalsPage() {
  const { data, isLoading, isError, refetch } = useApprovals();
  const decide = useDecideApproval();
  const user = useAuthStore((s) => s.user);

  async function onDecide(
    deliverableId: string,
    decision: Exclude<ApprovalStatus, "pending">,
  ) {
    await decide.mutateAsync({
      deliverableId,
      decision,
      actor: user?.id ?? "insp.authority@mrpl.local",
    });
  }

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="HITL"
        title="Approvals"
        description="Human-in-the-loop review before deliverable finalisation."
      />

      <div
        className="border border-warning/35 bg-warning-soft px-3 py-2.5 flex items-start gap-2 text-[12.5px] text-warning"
        role="status"
      >
        <AlertTriangle className="size-3.5 shrink-0 mt-0.5" aria-hidden />
        <p>
          Human approval required before finalisation. Local agents stage
          artefacts; Inspection Authority must approve, request changes, or
          reject.
        </p>
      </div>

      {isLoading ? <LoadingState label="Loading pending approvals…" /> : null}
      {isError ? (
        <ErrorState
          title="Approvals unavailable"
          onRetry={() => void refetch()}
        />
      ) : null}

      {!isLoading && !isError && data && data.length === 0 ? (
        <EmptyState
          title="No pending approvals"
          description="Queued human gates will appear here when deliverables require sign-off."
        />
      ) : null}

      {!isLoading && !isError && data
        ? data.map((d) => (
            <section key={d.id} className="border border-border bg-panel">
              <SectionLabel>
                {d.name} · {d.approvalStatus.replace(/_/g, " ")}
              </SectionLabel>
              <div className="p-3 space-y-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 rail pl-3">
                    <h2 className="text-[14px] font-semibold text-text">
                      {d.name}
                    </h2>
                    <p className="text-[12px] text-text-secondary mt-1">
                      Task: {d.taskTitle}
                    </p>
                    <p className="text-[12px] text-text-muted mt-2 leading-relaxed max-w-2xl">
                      {d.provenanceSummary}
                    </p>
                  </div>
                  <StatusBadge status={d.status} />
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-px bg-border border border-border text-[12px]">
                  <div className="bg-canvas px-3 py-2">
                    <div className="text-micro text-text-muted mb-0.5">
                      Evidence
                    </div>
                    <div className="font-mono text-text">{d.evidenceCount}</div>
                  </div>
                  <div className="bg-canvas px-3 py-2">
                    <div className="text-micro text-text-muted mb-0.5">
                      Created
                    </div>
                    <div className="font-mono text-text text-[11px]">
                      {formatDateTime(d.createdAt)}
                    </div>
                  </div>
                  <div className="bg-canvas px-3 py-2 col-span-2 sm:col-span-1">
                    <div className="text-micro text-text-muted mb-0.5">
                      Type
                    </div>
                    <div className="capitalize text-text">{d.type}</div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-border">
                  <Button
                    variant="primary"
                    size="sm"
                    disabled={decide.isPending}
                    onClick={() => void onDecide(d.id, "approved")}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="warning"
                    size="sm"
                    disabled={decide.isPending}
                    onClick={() => void onDecide(d.id, "changes_requested")}
                  >
                    Request changes
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    disabled={decide.isPending}
                    onClick={() => void onDecide(d.id, "rejected")}
                  >
                    Reject
                  </Button>
                  <Link
                    to={`/evidence?taskId=${d.taskId}`}
                    className="text-[12px] text-accent hover:underline ml-auto"
                  >
                    Open evidence →
                  </Link>
                </div>
              </div>
            </section>
          ))
        : null}
    </div>
  );
}
