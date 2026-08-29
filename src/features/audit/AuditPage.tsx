import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Field, Input } from "@/components/ui/Field";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  SectionLabel,
} from "@/components/common/States";
import { useAuditEvents } from "@/hooks";
import { cn, formatClock, formatDateTime } from "@/lib/utils";

export function AuditPage() {
  const { data, isLoading, isError, refetch } = useAuditEvents();
  const [query, setQuery] = useState("");
  const [eventType, setEventType] = useState("all");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const types = useMemo(() => {
    const set = new Set<string>();
    data?.forEach((e) => set.add(e.eventType));
    return Array.from(set).sort();
  }, [data]);

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = query.trim().toLowerCase();
    return data
      .filter((e) => (eventType === "all" ? true : e.eventType === eventType))
      .filter((e) => {
        if (!q) return true;
        return (
          e.action.toLowerCase().includes(q) ||
          e.result.toLowerCase().includes(q) ||
          e.actor.toLowerCase().includes(q) ||
          (e.details?.toLowerCase().includes(q) ?? false)
        );
      })
      .slice()
      .sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  }, [data, query, eventType]);

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Ledger"
        title="Audit"
        description="Filterable event timeline for task, model, sovereignty, and approval actions."
      />

      <div className="border border-border bg-panel p-3 grid grid-cols-1 sm:grid-cols-[1fr_200px] gap-3">
        <Field label="Filter">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search action, actor, result…"
          />
        </Field>
        <Field label="Event type">
          <Select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
          >
            <option value="all">All types</option>
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
        </Field>
      </div>

      {isLoading ? <LoadingState label="Loading audit events…" /> : null}
      {isError ? (
        <ErrorState title="Audit unavailable" onRetry={() => void refetch()} />
      ) : null}

      {!isLoading && !isError && filtered.length === 0 ? (
        <EmptyState title="No matching events" />
      ) : null}

      {!isLoading && !isError && filtered.length > 0 ? (
        <section className="border border-border bg-panel">
          <SectionLabel>
            Events · {filtered.length}
            {data && filtered.length !== data.length
              ? ` of ${data.length}`
              : ""}
          </SectionLabel>
          <ul className="divide-y divide-border">
            {filtered.map((ev) => {
              const open = expanded[ev.id] ?? false;
              return (
                <li key={ev.id}>
                  <button
                    type="button"
                    className="w-full text-left px-3 py-2.5 flex gap-3 hover:bg-raised/40"
                    onClick={() =>
                      setExpanded((s) => ({ ...s, [ev.id]: !open }))
                    }
                  >
                    {open ? (
                      <ChevronDown className="size-3.5 text-text-muted mt-1 shrink-0" />
                    ) : (
                      <ChevronRight className="size-3.5 text-text-muted mt-1 shrink-0" />
                    )}
                    <div className="font-mono text-[10px] text-text-muted w-[72px] shrink-0 pt-0.5">
                      {formatClock(ev.timestamp)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[12px] font-medium text-text">
                          {ev.action}
                        </span>
                        <span className="text-micro text-text-muted">
                          {ev.eventType}
                        </span>
                        <StatusBadge status={ev.status} compact />
                      </div>
                      <p className="text-[12px] text-text-secondary mt-0.5">
                        {ev.result}
                      </p>
                      <div className="text-[10px] text-text-muted mt-0.5 font-mono">
                        {ev.actor}
                        {ev.taskId ? ` · ${ev.taskId}` : ""}
                      </div>
                    </div>
                  </button>
                  {open ? (
                    <div
                      className={cn(
                        "px-3 pb-3 pl-10 text-[11px] text-text-secondary space-y-1",
                      )}
                    >
                      <div>Time: {formatDateTime(ev.timestamp)}</div>
                      {ev.modelId ? <div>Model: {ev.modelId}</div> : null}
                      {ev.toolId ? <div>Tool: {ev.toolId}</div> : null}
                      {ev.evidenceIds?.length ? (
                        <div>Evidence: {ev.evidenceIds.join(", ")}</div>
                      ) : null}
                      {ev.details ? (
                        <p className="leading-relaxed">{ev.details}</p>
                      ) : null}
                      {ev.policyDecision ? (
                        <div className="border border-border bg-canvas px-2 py-1.5 mt-1">
                          <div className="text-micro text-text-muted mb-1">
                            Policy decision
                          </div>
                          <div>
                            {ev.policyDecision.decision} —{" "}
                            {ev.policyDecision.reason}
                          </div>
                          <div className="font-mono text-[10px] text-text-muted mt-0.5">
                            {ev.policyDecision.policyName} ·{" "}
                            {ev.policyDecision.resource}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
