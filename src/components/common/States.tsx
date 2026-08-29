import type { ReactNode } from "react";
import { AlertTriangle, Ban, FileQuestion, Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

export function LoadingState({
  label = "Loading…",
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 px-3 py-10 text-[12.5px] text-text-secondary",
        className,
      )}
      role="status"
    >
      <Loader2 className="size-3.5 animate-spin text-running" aria-hidden />
      {label}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
  className,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-start gap-1.5 border border-dashed border-border px-4 py-8 bg-surface/40",
        className,
      )}
    >
      <div className="flex items-center gap-2 text-text-secondary">
        <FileQuestion className="size-3.5" aria-hidden />
        <p className="text-[13px] font-medium text-text">{title}</p>
      </div>
      {description ? (
        <p className="text-[11.5px] text-text-muted max-w-md leading-relaxed">
          {description}
        </p>
      ) : null}
      {action}
    </div>
  );
}

export function ErrorState({
  title = "Unable to load data",
  description,
  onRetry,
  className,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-start gap-2 border border-danger/35 bg-danger-soft px-4 py-5",
        className,
      )}
      role="alert"
    >
      <div className="flex items-center gap-2 text-danger">
        <AlertTriangle className="size-3.5" aria-hidden />
        <p className="text-[13px] font-medium">{title}</p>
      </div>
      {description ? (
        <p className="text-[11.5px] text-text-secondary leading-relaxed">
          {description}
        </p>
      ) : null}
      {onRetry ? (
        <Button size="sm" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}

export function BlockedState({
  title = "Action blocked by Sovereignty Policy",
  description,
  className,
}: {
  title?: string;
  description?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-start gap-2 border border-blocked/35 bg-blocked-soft px-4 py-5",
        className,
      )}
      role="status"
    >
      <div className="flex items-center gap-2 text-blocked">
        <Ban className="size-3.5" aria-hidden />
        <p className="text-[13px] font-medium">{title}</p>
      </div>
      {description ? (
        <p className="text-[11.5px] text-text-secondary leading-relaxed">
          {description}
        </p>
      ) : null}
    </div>
  );
}

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-3 pb-3 mb-1 border-b border-border">
      <div className="min-w-0 rail pl-3">
        {eyebrow ? (
          <p className="text-micro text-text-muted mb-1">{eyebrow}</p>
        ) : null}
        <h1 className="text-[17px] font-semibold tracking-tight text-text leading-none">
          {title}
        </h1>
        {description ? (
          <p className="mt-1.5 text-[11.5px] text-text-muted max-w-2xl leading-relaxed">
            {description}
          </p>
        ) : null}
      </div>
      {actions ? (
        <div className="flex items-center gap-2">{actions}</div>
      ) : null}
    </header>
  );
}

export function SectionLabel({
  children,
  right,
}: {
  children: ReactNode;
  right?: ReactNode;
}) {
  return (
    <div className="panel-header justify-between">
      <span>{children}</span>
      {right ? (
        <span className="normal-case tracking-normal font-normal">{right}</span>
      ) : null}
    </div>
  );
}

export function MetaRow({
  label,
  value,
  mono,
}: {
  label: string;
  value: ReactNode;
  mono?: boolean;
}) {
  return (
    <div className="grid grid-cols-[108px_1fr] gap-2 text-[12px] py-1.5 border-b border-border/60 last:border-0">
      <dt className="text-text-muted">{label}</dt>
      <dd
        className={cn("text-text break-words", mono && "font-mono text-[11px]")}
      >
        {value}
      </dd>
    </div>
  );
}
