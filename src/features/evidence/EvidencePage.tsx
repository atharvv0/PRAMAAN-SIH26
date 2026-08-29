import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import type { EvidenceRecord } from "@/types/evidence";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  MetaRow,
  PageHeader,
  SectionLabel,
} from "@/components/common/States";
import { useEvidence, useEvidenceItem } from "@/hooks";
import { cn, formatClock } from "@/lib/utils";

export function EvidencePage() {
  const { id: routeId } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const runId = searchParams.get("runId") ?? undefined;
  const taskId = searchParams.get("taskId") ?? undefined;

  const listQuery = useEvidence(taskId, runId);
  const [selectedId, setSelectedId] = useState<string | undefined>(routeId);

  useEffect(() => {
    if (routeId) {
      setSelectedId(routeId);
      return;
    }
    if (listQuery.data && listQuery.data.length > 0 && !selectedId) {
      setSelectedId(listQuery.data[0].id);
    }
  }, [routeId, listQuery.data, selectedId]);

  const itemQuery = useEvidenceItem(selectedId ?? "");
  const selected =
    itemQuery.data ?? listQuery.data?.find((e) => e.id === selectedId) ?? null;

  if (listQuery.isLoading) {
    return <LoadingState label="Loading evidence ledger…" />;
  }

  if (listQuery.isError || !listQuery.data) {
    return (
      <ErrorState
        title="Evidence unavailable"
        onRetry={() => void listQuery.refetch()}
      />
    );
  }

  const records = listQuery.data;

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Investigation"
        title="Evidence"
        description="Claim → source → page → region → model/tool → validation."
      />

      {records.length === 0 ? (
        <EmptyState
          title="No evidence captured"
          description="Evidence appears as OCR, retrieval, and spreadsheet steps complete."
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)] gap-3 min-h-[540px] border border-border bg-panel">
          <section className="flex flex-col min-h-0 border-b lg:border-b-0 lg:border-r border-border">
            <SectionLabel
              right={
                <span className="font-mono text-[10px] text-text-muted">
                  {records.length}
                </span>
              }
            >
              Claims
            </SectionLabel>
            <ul className="overflow-y-auto divide-y divide-border flex-1">
              {records.map((ev) => (
                <li key={ev.id}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(ev.id)}
                    className={cn(
                      "w-full text-left px-3 py-2.5 transition-colors relative",
                      selectedId === ev.id ? "bg-raised" : "hover:bg-raised/40",
                    )}
                  >
                    {selectedId === ev.id ? (
                      <span
                        className="absolute left-0 top-0 bottom-0 w-0.5 bg-accent"
                        aria-hidden
                      />
                    ) : null}
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-[10px] text-text-muted">
                        {ev.id}
                      </span>
                      <ValidationChip status={ev.validationStatus} />
                    </div>
                    <p className="mt-1 text-[12px] text-text line-clamp-3 leading-snug">
                      {ev.claim}
                    </p>
                    <div className="mt-1 text-[10px] text-text-muted truncate font-mono">
                      {ev.sourceDocument} · p.{ev.page}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <section className="flex flex-col min-h-0">
            <SectionLabel>Claim inspector</SectionLabel>
            {selected ? (
              <ClaimDetail record={selected} />
            ) : (
              <EmptyState title="Select a claim" className="m-3 border-0" />
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function ClaimDetail({ record }: { record: EvidenceRecord }) {
  const chain = useMemo(
    () => [
      { label: "CLAIM", value: record.claim },
      { label: "SOURCE", value: record.sourceDocument },
      { label: "PAGE", value: String(record.page) },
      {
        label: "REGION",
        value: `x=${record.region.x.toFixed(2)} y=${record.region.y.toFixed(2)} w=${record.region.w.toFixed(2)} h=${record.region.h.toFixed(2)}`,
      },
      {
        label: "MODEL / TOOL",
        value:
          [record.modelId, record.toolId].filter(Boolean).join(" · ") || "—",
      },
      {
        label: "VALIDATION",
        value: record.validationStatus,
      },
    ],
    [record],
  );

  return (
    <div className="p-3 grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_260px] gap-3 flex-1 min-h-0">
      <div className="space-y-3 min-w-0">
        <ol className="border border-border bg-canvas">
          {chain.map((step, i) => (
            <li
              key={step.label}
              className={cn(
                "px-3 py-2 flex gap-3",
                i < chain.length - 1 && "border-b border-border",
              )}
            >
              <div className="shrink-0 w-5 flex flex-col items-center pt-0.5">
                <span
                  className={cn(
                    "size-2 border",
                    i === chain.length - 1
                      ? "bg-accent border-accent"
                      : "bg-raised border-border-strong",
                  )}
                />
                {i < chain.length - 1 ? (
                  <span className="w-px flex-1 bg-border mt-1 min-h-[12px]" />
                ) : null}
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-micro text-accent mb-0.5">
                  {step.label}
                </div>
                <div
                  className={cn(
                    "text-[12.5px] text-text leading-relaxed",
                    (step.label === "REGION" ||
                      step.label === "MODEL / TOOL") &&
                      "font-mono text-[11px]",
                  )}
                >
                  {step.value}
                </div>
              </div>
            </li>
          ))}
        </ol>

        <div className="border border-border px-3 py-2 bg-surface/40">
          <div className="text-micro text-text-muted mb-1">Extracted text</div>
          <p className="text-[12px] text-text-secondary leading-relaxed font-mono">
            {record.extractedText}
          </p>
        </div>

        <dl className="px-1">
          <MetaRow
            label="Confidence"
            value={`${(record.confidence * 100).toFixed(1)}%`}
            mono
          />
          <MetaRow
            label="Captured"
            value={formatClock(record.createdAt)}
            mono
          />
          <MetaRow label="Run" value={record.runId} mono />
        </dl>
      </div>

      <div>
        <div className="text-micro text-text-muted mb-2">Source region</div>
        <SourceRegionViewer
          documentName={record.sourceDocument}
          page={record.page}
          region={record.region}
        />
      </div>
    </div>
  );
}

function SourceRegionViewer({
  documentName,
  page,
  region,
}: {
  documentName: string;
  page: number;
  region: EvidenceRegion;
}) {
  return (
    <div className="border border-border bg-canvas p-2">
      <div className="text-[10px] text-text-muted mb-2 truncate font-mono">
        {documentName} · page {page}
      </div>
      <div className="relative aspect-[3/4] max-h-[340px] bg-surface border border-border overflow-hidden">
        <div className="absolute inset-3 space-y-1.5 opacity-35 pointer-events-none">
          {Array.from({ length: 18 }).map((_, i) => (
            <div
              key={i}
              className="h-1 bg-border-strong"
              style={{ width: `${55 + ((i * 17) % 40)}%` }}
            />
          ))}
        </div>
        <div
          className="absolute border-2 border-accent bg-accent-soft/50"
          style={{
            left: `${region.x * 100}%`,
            top: `${region.y * 100}%`,
            width: `${region.w * 100}%`,
            height: `${region.h * 100}%`,
          }}
          title="Grounded region"
        />
      </div>
      <p className="mt-2 text-[10px] text-text-muted leading-relaxed">
        Region overlay on document placeholder (demo). Coordinates normalized
        0–1.
      </p>
    </div>
  );
}

function ValidationChip({
  status,
}: {
  status: EvidenceRecord["validationStatus"];
}) {
  const tone =
    status === "validated"
      ? "text-success border-success/30 bg-success-soft"
      : status === "rejected"
        ? "text-danger border-danger/30 bg-danger-soft"
        : "text-warning border-warning/30 bg-warning-soft";

  return (
    <span
      className={cn(
        "text-[10px] px-1.5 py-0.5 border font-medium capitalize",
        tone,
      )}
    >
      {status}
    </span>
  );
}
