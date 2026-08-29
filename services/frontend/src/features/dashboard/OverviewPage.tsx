import { Link } from "react-router-dom";
import type { ReactNode } from "react";
import { Activity, ArrowRight, CheckCircle2, ShieldCheck } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { DataTable, Td } from "@/components/common/DataTable";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  MetaRow,
  PageHeader,
  SectionLabel,
} from "@/components/common/States";
import {
  HealthIndicator,
  SovereigntyIndicator,
} from "@/components/common/Indicators";
import { useOverview } from "@/hooks";
import { formatClock, formatDateTime } from "@/lib/utils";

export function OverviewPage() {
  const query = useOverview();
  if (query.isLoading)
    return <LoadingState label="Loading live operational state…" />;
  if (query.isError || !query.data)
    return (
      <ErrorState
        title="Overview unavailable"
        description="The local API did not return an operational snapshot. PRAMAAN is not substituting synthetic metrics."
        onRetry={() => void query.refetch()}
      />
    );
  const data = query.data;
  const sov = data.sovereignty;
  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="Operations"
        title="Operational overview"
        description="A live command surface for work, human gates, model availability, and sovereign network state."
        actions={
          <>
            <HealthIndicator />
            <Link
              to="/tasks/new"
              className="inline-flex h-8 items-center border border-accent bg-accent px-3 text-[12px] font-semibold text-canvas hover:brightness-110"
            >
              New task
            </Link>
          </>
        }
      />
      <div className="grid gap-px border border-border bg-border sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Metric
          label="Sovereignty"
          value={
            <SovereigntyIndicator compact active={sov.mode === "active"} />
          }
        />
        <Metric
          label="Local processing"
          value={`${sov.localProcessingPercent}%`}
          mono
        />
        <Metric
          label="Local models"
          value={`${sov.healthyModels}/${sov.totalModels}`}
          mono
        />
        <Metric label="Active tasks" value={data.activeTasks} mono />
        <Metric
          label="Pending approvals"
          value={data.pendingApprovals}
          mono
          emphasis
        />
        <Metric
          label="Blocked egress"
          value={sov.externalBlocked}
          mono
          warning
        />
      </div>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,.65fr)]">
        <section className="border border-border bg-panel">
          <SectionLabel
            right={
              <Link to="/tasks" className="text-accent">
                All tasks
              </Link>
            }
          >
            Active work
          </SectionLabel>
          {data.currentTasks.length === 0 ? (
            <EmptyState
              className="m-4"
              title="No active work"
              description="The API reports no current tasks. Start a new task when work is ready."
              action={
                <Link
                  to="/tasks/new"
                  className="inline-flex h-7 items-center border border-border bg-raised px-2.5 text-[11px] font-medium text-text hover:bg-hover"
                >
                  Create task
                </Link>
              }
            />
          ) : (
            <DataTable
              columns={[
                "Task",
                "Workspace",
                "Status",
                "Progress",
                "Current step",
                "Updated",
              ]}
              className="border-0"
            >
              {data.currentTasks.map((task) => (
                <tr key={task.id} className="hover:bg-raised/50">
                  <Td>
                    <Link
                      to={task.runId ? `/runs/${task.runId}` : "/tasks"}
                      className="font-medium text-text hover:text-accent"
                    >
                      {task.title}
                    </Link>
                  </Td>
                  <Td>{task.workspaceName}</Td>
                  <Td>
                    <StatusBadge status={task.status} compact />
                  </Td>
                  <Td mono>{task.progress}%</Td>
                  <Td>{task.currentStep ?? "—"}</Td>
                  <Td mono>{formatClock(task.updatedAt)}</Td>
                </tr>
              ))}
            </DataTable>
          )}
        </section>
        <div className="space-y-4">
          <section className="border border-border bg-panel">
            <SectionLabel>Control posture</SectionLabel>
            <dl className="px-4 py-2">
              <MetaRow
                label="Sovereignty mode"
                value={sov.mode.toUpperCase()}
              />
              <MetaRow
                label="Egress policy"
                value={sov.egressPolicy.replace(/_/g, " ")}
              />
              <MetaRow
                label="Audit recording"
                value={sov.auditRecording ? "Enabled" : "Disabled"}
              />
              <MetaRow
                label="Healthy models"
                value={`${sov.healthyModels} / ${sov.totalModels}`}
                mono
              />
            </dl>
          </section>
          <section className="border border-border bg-panel">
            <SectionLabel>Recent activity</SectionLabel>
            {data.activity.length === 0 ? (
              <EmptyState className="m-3" title="No activity returned" />
            ) : (
              <ul className="divide-y divide-border">
                {data.activity.slice(0, 6).map((item) => (
                  <li key={item.id} className="px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-mono text-[10px] text-text-muted">
                        {formatClock(item.timestamp)}
                      </span>
                      <StatusBadge status={item.status} compact />
                    </div>
                    <div className="mt-1 text-[12px] font-medium text-text">
                      {item.action}
                    </div>
                    <div className="mt-0.5 text-[11px] leading-relaxed text-text-muted">
                      {item.result}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
      <section className="border border-border bg-panel">
        <SectionLabel
          right={
            <Link to="/sovereignty" className="text-accent">
              Sovereignty console
            </Link>
          }
        >
          Network boundary
        </SectionLabel>
        {data.networkEvents.length === 0 ? (
          <EmptyState
            className="m-3"
            title="No network events returned"
            description="An empty result is different from an offline API: the backend responded successfully with no events."
          />
        ) : (
          <ul className="divide-y divide-border">
            {data.networkEvents.slice(0, 8).map((event) => (
              <li
                key={event.id}
                className="flex flex-wrap gap-3 px-4 py-3 text-[11.5px]"
              >
                <span className="w-[72px] shrink-0 font-mono text-[10px] text-text-muted">
                  {formatClock(event.timestamp)}
                </span>
                <span className="w-[120px] shrink-0 text-micro text-text-muted">
                  {event.kind.replace(/_/g, " ")}
                </span>
                <div className="min-w-[180px] flex-1">
                  <div className="text-text-secondary">{event.message}</div>
                  {event.destination ? (
                    <div className="mt-1 truncate font-mono text-[10px] text-text-muted">
                      {event.destination}
                    </div>
                  ) : null}
                </div>
                {event.decision ? (
                  <span
                    className={
                      event.decision === "blocked"
                        ? "font-semibold text-blocked"
                        : "font-semibold text-success"
                    }
                  >
                    {event.decision.toUpperCase()}
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        <div className="border-t border-border px-4 py-2 text-[10px] text-text-muted">
          Latest observation · {formatDateTime(new Date().toISOString())}
        </div>
      </section>
      <div className="grid gap-3 md:grid-cols-3">
        <Callout
          icon={<ShieldCheck />}
          title="Local-first"
          text="Model and tool execution remains subject to the backend sovereignty policy."
        />
        <Callout
          icon={<CheckCircle2 />}
          title="Human control"
          text="Approval-required states are surfaced instead of silently finalising outputs."
        />
        <Callout
          icon={<Activity />}
          title="Traceable"
          text="Runs, evidence, deliverables, and audit events are separate first-class records."
        />
      </div>
    </div>
  );
}
function Metric({
  label,
  value,
  mono = false,
  emphasis = false,
  warning = false,
}: {
  label: string;
  value: ReactNode;
  mono?: boolean;
  emphasis?: boolean;
  warning?: boolean;
}) {
  return (
    <div className="bg-panel px-4 py-3.5">
      <div className="text-micro text-text-muted">{label}</div>
      <div
        className={`mt-2 text-[16px] font-semibold ${mono ? "font-mono tabular" : ""} ${emphasis ? "text-warning" : warning ? "text-blocked" : "text-text"}`}
      >
        {value}
      </div>
    </div>
  );
}
function Callout({
  icon,
  title,
  text,
}: {
  icon: ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="border border-border bg-surface px-4 py-3">
      <div className="flex items-center gap-2 text-accent">
        <span className="grid size-6 place-items-center border border-accent/30 bg-accent-soft">
          {icon}
        </span>
        <span className="text-[12px] font-semibold text-text">{title}</span>
      </div>
      <p className="mt-2 text-[10.5px] leading-relaxed text-text-muted">
        {text}
      </p>
      <ArrowRight className="mt-2 size-3 text-text-muted" aria-hidden />
    </div>
  );
}
