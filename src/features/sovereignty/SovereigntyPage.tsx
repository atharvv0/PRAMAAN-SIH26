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
  { id: "configure", label: "Configure", state: "ACTIVE" },
  { id: "enforce", label: "Enforce", state: "ACTIVE" },
  { id: "observe", label: "Observe", state: "ACTIVE" },
  { id: "audit", label: "Audit", state: "ACTIVE" },
  { id: "demonstrate", label: "Demonstrate", state: "LIVE" },
] as const;

export function SovereigntyPage() {
  const sovQuery = useSovereignty();
  const netQuery = useNetworkEvents();
  const retrySovereignty = () => {
    void sovQuery.refetch();
    void netQuery.refetch();
  };

  if (sovQuery.isLoading || netQuery.isLoading) {
    return <LoadingState label="Loading sovereignty console…" />;
  }

  if (sovQuery.isError || !sovQuery.data) {
    return (
      <ErrorState
        title="Sovereignty status unavailable"
        onRetry={() => void sovQuery.refetch()}
      />
    );
  }

  const sov = sovQuery.data;
  const events = netQuery.data ?? [];
  const blockedEvents = events.filter((e) => e.decision === "blocked");

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Control plane"
        title="Sovereignty"
        description="Observable egress policy, local processing, and audit — not a claim of absolute security."
      />

      {/* Pipeline as control stages */}
      <div className="border border-border bg-panel">
        <SectionLabel>Policy lifecycle</SectionLabel>
        <div className="grid grid-cols-2 sm:grid-cols-5">
          {POLICY_PIPELINE.map((stage, i) => (
            <div
              key={stage.id}
              className={cn(
                "px-3 py-3 border-border",
                i < POLICY_PIPELINE.length - 1 && "sm:border-r",
                i % 2 === 0 && "border-r sm:border-r",
                i < 2 && "border-b sm:border-b-0",
                i === 2 && "border-b sm:border-b-0 col-span-2 sm:col-span-1",
              )}
            >
              <div className="font-mono text-[10px] text-text-muted">
                {String(i + 1).padStart(2, "0")}
              </div>
              <div className="text-[13px] font-semibold text-text mt-0.5">
                {stage.label}
              </div>
              <div
                className={cn(
                  "text-[10px] font-semibold mt-1.5 tracking-wide",
                  stage.state === "LIVE" ? "text-running" : "text-success",
                )}
              >
                {stage.state}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)] gap-3">
        <section className="border border-border bg-panel self-start">
          <SectionLabel>Network boundary</SectionLabel>
          <div className="p-3 space-y-3">
            <div className="flex items-center gap-2">
              <SovereigntyIndicator active={sov.mode === "active"} />
              <span className="text-[11px] text-text-secondary uppercase tracking-wide">
                {sov.mode}
              </span>
            </div>

            <div className="border border-border bg-canvas divide-y divide-border text-[12px]">
              <BoundaryRow
                label="Status"
                value={
                  <span className="text-success font-semibold">ACTIVE</span>
                }
              />
              <BoundaryRow
                label="Egress"
                value={
                  <span className="text-blocked font-semibold tracking-wide">
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
                  <span className="font-mono tabular text-blocked text-[14px] font-semibold">
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

            <p className="text-[11px] text-text-muted leading-relaxed border-l-2 border-accent/50 pl-2.5">
              Honest posture: sovereignty reduces egress risk and keeps
              processing local where configured. Operators must still review
              blocked events, model health, and audit seals.
            </p>
          </div>
        </section>

        <section className="border border-border bg-panel flex flex-col min-h-[440px]">
          <SectionLabel
            right={
              <span className="font-mono text-[10px] text-blocked">
                {blockedEvents.length} blocked
              </span>
            }
          >
            Live network timeline
          </SectionLabel>
          {netQuery.isError ? (
            <ErrorState
              title="Network events unavailable"
              className="m-3"
              onRetry={() => void netQuery.refetch()}
            />
          ) : events.length === 0 ? (
            <EmptyState title="No network events" className="m-3" />
          ) : (
            <ul className="overflow-y-auto divide-y divide-border flex-1">
              {events.map((ev) => {
                const blocked = ev.decision === "blocked";
                return (
                  <li
                    key={ev.id}
                    className={cn(
                      "px-3 py-2.5 flex gap-3 text-[12px] relative",
                      blocked && "bg-blocked-soft/25",
                    )}
                  >
                    {blocked ? (
                      <span
                        className="absolute left-0 top-0 bottom-0 w-0.5 bg-blocked"
                        aria-hidden
                      />
                    ) : null}
                    <div className="font-mono text-[10px] text-text-muted w-[64px] shrink-0 pt-0.5">
                      {formatClock(ev.timestamp)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-micro text-text-secondary">
                          {ev.kind.replace(/_/g, " ")}
                        </span>
                        {ev.decision ? (
                          <span
                            className={cn(
                              "text-[10px] font-semibold uppercase tracking-wide",
                              blocked ? "text-blocked" : "text-success",
                            )}
                          >
                            {ev.decision}
                          </span>
                        ) : null}
                      </div>
                      <p className="text-text-secondary mt-0.5 leading-relaxed">
                        {ev.message}
                      </p>
                      {ev.destination ? (
                        <div className="font-mono text-[10px] text-text-muted mt-1 truncate">
                          {ev.destination}
                        </div>
                      ) : null}
                      {ev.reason ? (
                        <div className="text-[11px] text-text-muted mt-0.5">
                          {ev.reason}
                        </div>
                      ) : null}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
          <div className="border-t border-border px-3 py-1.5 text-[10px] text-text-muted font-mono">
            Polling 4s · blocked in view {blockedEvents.length}
          </div>
        </section>
      </div>
    </div>
  );
}

function BoundaryRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 px-3 py-2">
      <span className="text-text-muted">{label}</span>
      <span className="text-text text-right">{value}</span>
    </div>
  );
}
