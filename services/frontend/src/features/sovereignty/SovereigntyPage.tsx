import type { ReactNode } from "react";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  SectionLabel,
} from "@/components/common/States";
import { SovereigntyIndicator } from "@/components/common/Indicators";
import { useNetworkEvents, useSovereignty } from "@/hooks";
import { cn, formatClock } from "@/lib/utils";

const POLICY_PIPELINE = [
  { id: "boundary", label: "Boundary", note: "Network policy" },
  { id: "execution", label: "Execution", note: "Local runtime" },
  { id: "observation", label: "Observation", note: "Network events" },
  { id: "audit", label: "Audit", note: "Recorded state" },
] as const;

export function SovereigntyPage() {
  const sovQuery = useSovereignty();
  const netQuery = useNetworkEvents();

  if (sovQuery.isLoading) {
    return <LoadingState label="Loading sovereignty console…" />;
  }

  if (sovQuery.isError) {
    return (
      <ErrorState
        title="Sovereignty status unavailable"
        description="The local API did not return the sovereignty snapshot."
        onRetry={() => void sovQuery.refetch()}
      />
    );
  }

  if (!sovQuery.data) {
    return (
      <ErrorState
        title="Sovereignty status unavailable"
        description="No sovereignty snapshot was returned by the local API."
        onRetry={() => void sovQuery.refetch()}
      />
    );
  }

  const sov = sovQuery.data;

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Control plane"
        title="Sovereignty"
        description="Observable egress policy, local processing, and audit — not a claim of absolute security."
      />

      <div className="border border-border bg-panel">
        <SectionLabel>Policy lifecycle</SectionLabel>

        <div className="grid grid-cols-2 lg:grid-cols-4">
          {POLICY_PIPELINE.map((stage, i) => (
            <div
              key={stage.id}
              className={cn(
                "border-border px-3 py-3",
                i < POLICY_PIPELINE.length - 1 && "lg:border-r",
                i % 2 === 0 && "border-r lg:border-r-0",
                i < 2 && "border-b lg:border-b-0",
                i === 2 && "border-b lg:border-b-0",
              )}
            >
              <div className="font-mono text-[10px] text-text-muted">
                {String(i + 1).padStart(2, "0")}
              </div>

              <div className="mt-0.5 text-[13px] font-semibold text-text">
                {stage.label}
              </div>

              <div
                className={cn(
                  "mt-1.5 text-[10px] font-semibold tracking-wide",
                  stage.id === "boundary" ? "text-accent" : "text-success",
                )}
              >
                {stage.note}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[320px_minmax(0,1fr)]">
        <section className="border border-border bg-panel self-start">
          <SectionLabel>Network boundary</SectionLabel>

          <div className="space-y-3 p-3">
            <div className="flex items-center gap-2">
              <SovereigntyIndicator active={sov.mode === "active"} />

              <span className="text-[11px] uppercase tracking-wide text-text-secondary">
                {sov.mode}
              </span>
            </div>

            <div className="divide-y divide-border border border-border bg-canvas text-[12px]">
              <BoundaryRow
                label="Status"
                value={
                  <span
                    className={
                      sov.mode === "active"
                        ? "font-semibold text-success"
                        : "text-text-muted"
                    }
                  >
                    {sov.mode.toUpperCase()}
                  </span>
                }
              />

              <BoundaryRow
                label="Egress"
                value={
                  <span className="font-semibold tracking-wide text-blocked">
                    {sov.egressPolicy === "deny_by_default"
                      ? "DENY BY DEFAULT"
                      : "ALLOWLIST"}
                  </span>
                }
              />

              <BoundaryRow
                label="Allowed"
                value={
                  <span className="font-mono tabular">
                    {sov.externalAllowed}
                  </span>
                }
              />

              <BoundaryRow
                label="Blocked"
                value={
                  <span className="font-mono tabular text-[14px] font-semibold text-blocked">
                    {sov.externalBlocked}
                  </span>
                }
              />

              <BoundaryRow
                label="Local processing"
                value={
                  <span className="font-mono tabular">
                    {sov.localProcessingPercent}%
                  </span>
                }
              />

              <BoundaryRow
                label="Audit recording"
                value={
                  <span
                    className={
                      sov.auditRecording ? "text-success" : "text-text-muted"
                    }
                  >
                    {sov.auditRecording ? "ON" : "OFF"}
                  </span>
                }
              />

              <BoundaryRow
                label="Healthy models"
                value={
                  <span className="font-mono tabular">
                    {sov.healthyModels}/{sov.totalModels}
                  </span>
                }
              />
            </div>

            <p className="border-l-2 border-accent/50 pl-2.5 text-[11px] leading-relaxed text-text-muted">
              Honest posture: sovereignty reduces egress risk and keeps
              processing local where configured. Operators must still review
              blocked events, model health, and audit seals.
            </p>
          </div>
        </section>

        <section className="flex min-h-[440px] flex-col border border-border bg-panel">
          <SectionLabel
            right={
              <span className="font-mono text-[10px] text-blocked">
                {netQuery.data?.filter((event) => event.decision === "blocked")
                  .length ?? 0}{" "}
                blocked
              </span>
            }
          >
            Live network timeline
          </SectionLabel>

          {netQuery.isLoading ? (
            <LoadingState label="Loading network events…" className="m-3" />
          ) : netQuery.isError ? (
            <ErrorState
              title="Network events unavailable"
              description="The sovereignty snapshot is available, but the local API did not return the network event stream."
              className="m-3"
              onRetry={() => void netQuery.refetch()}
            />
          ) : (
            <NetworkTimeline events={netQuery.data ?? []} />
          )}

          <NetworkTimelineFooter
            blockedEvents={
              netQuery.data?.filter((event) => event.decision === "blocked")
                .length ?? 0
            }
          />
        </section>
      </div>
    </div>
  );
}

function NetworkTimeline({
  events,
}: {
  events: Array<{
    id: string;
    timestamp: string;
    kind: string;
    decision?: string | null;
    message: string;
    destination?: string | null;
    reason?: string | null;
  }>;
}) {
  if (events.length === 0) {
    return <EmptyState title="No network events" className="m-3" />;
  }

  return (
    <ul className="flex-1 divide-y divide-border overflow-y-auto">
      {events.map((event) => {
        const blocked = event.decision === "blocked";

        return (
          <li
            key={event.id}
            className={cn(
              "relative flex gap-3 px-3 py-2.5 text-[12px]",
              blocked && "bg-blocked-soft/25",
            )}
          >
            {blocked ? (
              <span
                className="absolute bottom-0 left-0 top-0 w-0.5 bg-blocked"
                aria-hidden="true"
              />
            ) : null}

            <div className="w-[64px] shrink-0 pt-0.5 font-mono text-[10px] text-text-muted">
              {formatClock(event.timestamp)}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-micro text-text-secondary">
                  {event.kind.replace(/_/g, " ")}
                </span>

                {event.decision ? (
                  <span
                    className={cn(
                      "text-[10px] font-semibold uppercase tracking-wide",
                      blocked ? "text-blocked" : "text-success",
                    )}
                  >
                    {event.decision}
                  </span>
                ) : null}
              </div>

              <p className="mt-0.5 leading-relaxed text-text-secondary">
                {event.message}
              </p>

              {event.destination ? (
                <div className="mt-1 truncate font-mono text-[10px] text-text-muted">
                  {event.destination}
                </div>
              ) : null}

              {event.reason ? (
                <div className="mt-0.5 text-[11px] text-text-muted">
                  {event.reason}
                </div>
              ) : null}
            </div>
          </li>
        );
      })}
    </ul>
  );
}

function NetworkTimelineFooter({ blockedEvents }: { blockedEvents: number }) {
  return (
    <div className="border-t border-border px-3 py-1.5 font-mono text-[10px] text-text-muted">
      Auto-refresh 4s · blocked events in view {blockedEvents}
    </div>
  );
}

function BoundaryRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 px-3 py-2">
      <span className="text-text-muted">{label}</span>
      <span className="text-right text-text">{value}</span>
    </div>
  );
}
