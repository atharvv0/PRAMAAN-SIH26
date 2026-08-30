import type {
  AgentStep,
  AgentState,
  ModelRouting,
  ToolInvocation,
} from "@/types/agent";
import type { AuditEvent } from "@/types/audit";
import type { Deliverable } from "@/types/deliverable";
import type { EvidenceRecord } from "@/types/evidence";
import type { ModelAdapter } from "@/types/model";
import type { DashboardOverview } from "@/types/overview";
import type { NetworkEvent, SovereigntyStatus } from "@/types/sovereignty";
import type { TaskDefinition, TaskFile } from "@/types/task";
import type { Workspace } from "@/types/workspace";
import { useAuthStore } from "@/store";

export interface CreateTaskInput {
  title: string;
  instruction: string;
  workspaceId: string;
  createdBy: string;
  sensitivity: "internal" | "confidential" | "restricted";
  file_ids?: string[];
}

export interface DecideApprovalInput {
  deliverableId: string;
  decision: "approved" | "changes_requested" | "rejected";
  actor: string;
  note?: string;
}

function normalizeBaseUrl(value: string | undefined): string {
  const raw = (value ?? "/api/v1").trim();
  if (!raw) return "/api/v1";
  return raw
    .replace(/^\[(.*)\]$/, "$1")
    .replace(/^<|>$/g, "")
    .replace(/^\(|\)$/g, "")
    .replace(/\/$/, "");
}

const baseUrl = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL as string | undefined,
);

export function apiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  return `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

function currentAuthEmail(): string | null {
  const user = useAuthStore.getState().user;
  const email = user?.email?.trim().toLowerCase();
  return email || null;
}

async function httpJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const email = currentAuthEmail();
  if (email) {
    headers.set("X-User-Email", email);
  }
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type"))
    headers.set("Content-Type", "application/json");

  let response: Response;
  try {
    response = await fetch(apiUrl(path), { ...init, headers });
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Unable to reach the local PRAMAAN API.";
    throw new ApiError(
      `Local API unavailable: ${message}`,
      0,
      "BACKEND_UNAVAILABLE",
    );
  }

  const text = await response.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    const errorBody = body as {
      error?: { message?: string; code?: string };
      detail?: string;
      message?: string;
    } | null;
    throw new ApiError(
      errorBody?.error?.message ??
        errorBody?.detail ??
        errorBody?.message ??
        `Request failed with HTTP ${response.status}`,
      response.status,
      errorBody?.error?.code,
    );
  }

  if (
    body &&
    typeof body === "object" &&
    "data" in body &&
    Object.keys(body).length <= 3
  ) {
    return (body as { data: T }).data;
  }
  return body as T;
}

function statusValue(value: unknown): TaskDefinition["status"] {
  const status = String(value ?? "queued");
  if (status === "awaiting_approval") return "approval_required";
  const allowed: TaskDefinition["status"][] = [
    "queued",
    "pending",
    "running",
    "success",
    "completed",
    "warning",
    "failed",
    "blocked",
    "approval_required",
    "offline",
    "sovereign",
    "external_blocked",
  ];
  return allowed.includes(status as TaskDefinition["status"])
    ? (status as TaskDefinition["status"])
    : "queued";
}

function fileType(name: string, mime?: string): TaskFile["type"] {
  const lower = name.toLowerCase();
  if (mime?.includes("pdf") || lower.endsWith(".pdf")) return "pdf";
  if (mime?.startsWith("image/") || /\.(png|jpe?g|webp|gif|svg)$/.test(lower))
    return "image";
  if (
    mime?.includes("spreadsheet") ||
    mime?.includes("excel") ||
    /\.(xlsx|xls|csv)$/.test(lower)
  )
    return "spreadsheet";
  if (mime?.includes("word") || /\.(docx?|txt|md)$/.test(lower))
    return "document";
  return "other";
}

function num(value: unknown, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function str(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function generatedId(prefix: string) {
  return typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
    ? `${prefix}-${crypto.randomUUID()}`
    : `${prefix}-${Date.now()}`;
}

function mapFile(file: Record<string, unknown>): TaskFile {
  const name = str(file.name ?? file.filename, "file");
  const mime =
    typeof file.type === "string"
      ? file.type
      : typeof file.mime === "string"
        ? file.mime
        : undefined;
  return {
    id: str(file.id ?? file.file_id, name),
    name,
    type: fileType(name, mime),
    sizeBytes: num(file.sizeBytes ?? file.size_bytes),
    status: statusValue(file.status),
    localProcessing: Boolean(
      file.localProcessing ?? file.local_processing ?? true,
    ),
  };
}

function mapTask(task: Record<string, unknown>): TaskDefinition {
  return {
    id: str(task.id ?? task.task_id, "unknown"),
    title: str(task.title, "PRAMAAN Task"),
    instruction: str(task.instruction ?? task.intent),
    workspaceId: str(task.workspaceId ?? task.workspace_id),
    workspaceName: str(task.workspaceName ?? task.workspace_name, "Workspace"),
    status: statusValue(task.status),
    progress: Math.max(0, Math.min(100, num(task.progress))),
    currentStep:
      typeof task.currentStep === "string"
        ? task.currentStep
        : typeof task.current_step === "string"
          ? task.current_step
          : undefined,
    model: typeof task.model === "string" ? task.model : undefined,
    createdBy: str(task.createdBy ?? task.created_by, "local operator"),
    createdAt: str(
      task.createdAt ?? task.created_at,
      new Date(0).toISOString(),
    ),
    updatedAt: str(
      task.updatedAt ?? task.updated_at,
      str(task.createdAt ?? task.created_at, new Date(0).toISOString()),
    ),
    elapsedMs: num(task.elapsedMs ?? task.elapsed_ms),
    files: Array.isArray(task.files)
      ? task.files.map((f) => mapFile(f as Record<string, unknown>))
      : [],
    runId:
      typeof task.runId === "string"
        ? task.runId
        : typeof task.run_id === "string"
          ? task.run_id
          : undefined,
  };
}

function mapRun(run: Record<string, unknown>): AgentState {
  const plan: AgentStep[] = (Array.isArray(run.plan) ? run.plan : []).map(
    (step) => {
      const s = step as Record<string, unknown>;
      return {
        id: str(s.id, "step"),
        label: str(s.label ?? s.name, "Step"),
        status: statusValue(s.status),
        startedAt:
          typeof s.startedAt === "string"
            ? s.startedAt
            : typeof s.started_at === "string"
              ? s.started_at
              : undefined,
        completedAt:
          typeof s.completedAt === "string"
            ? s.completedAt
            : typeof s.completed_at === "string"
              ? s.completed_at
              : undefined,
        durationMs: num(s.durationMs ?? s.duration_ms) || undefined,
        toolId:
          typeof s.toolId === "string"
            ? s.toolId
            : typeof s.tool_id === "string"
              ? s.tool_id
              : undefined,
        modelId:
          typeof s.modelId === "string"
            ? s.modelId
            : typeof s.model_id === "string"
              ? s.model_id
              : undefined,
        details: typeof s.details === "string" ? s.details : undefined,
        evidenceCount: num(s.evidenceCount ?? s.evidence_count) || undefined,
        warning: typeof s.warning === "string" ? s.warning : undefined,
        error: typeof s.error === "string" ? s.error : undefined,
      };
    },
  );

  const modelRoutings: ModelRouting[] = (
    Array.isArray(run.modelRoutings ?? run.model_routings)
      ? ((run.modelRoutings ?? run.model_routings) as unknown[])
      : []
  ).map((item) => {
    const m = item as Record<string, unknown>;
    return {
      stepId: str(m.stepId ?? m.step_id),
      taskLabel: str(m.taskLabel ?? m.task_label, "Step"),
      modelId: str(m.modelId ?? m.model_id),
      modelName: str(
        m.modelName ?? m.model_name,
        str(m.modelId ?? m.model_id, "Model"),
      ),
      reason: str(m.reason),
      local: Boolean(m.local ?? true),
      status: statusValue(m.status),
    };
  });

  const toolInvocations: ToolInvocation[] = (
    Array.isArray(run.toolInvocations ?? run.tool_invocations)
      ? ((run.toolInvocations ?? run.tool_invocations) as unknown[])
      : []
  ).map((item) => {
    const t = item as Record<string, unknown>;
    return {
      id: str(t.id, generatedId("tool")),
      tool: str(t.tool ?? t.name, "Tool"),
      status: statusValue(t.status),
      permission: t.permission === "blocked" ? "blocked" : "allowed",
      reason: str(t.reason),
      timestamp: str(
        t.timestamp ?? t.createdAt ?? t.created_at,
        new Date(0).toISOString(),
      ),
      durationMs: num(t.durationMs ?? t.duration_ms) || undefined,
      inputSummary:
        typeof t.inputSummary === "string"
          ? t.inputSummary
          : typeof t.input_summary === "string"
            ? t.input_summary
            : undefined,
      outputSummary:
        typeof t.outputSummary === "string"
          ? t.outputSummary
          : typeof t.output_summary === "string"
            ? t.output_summary
            : undefined,
    };
  });

  return {
    id: str(run.id ?? run.run_id),
    taskId: str(run.taskId ?? run.task_id),
    status: statusValue(run.status),
    currentStepId:
      typeof run.currentStepId === "string"
        ? run.currentStepId
        : typeof run.current_step_id === "string"
          ? run.current_step_id
          : undefined,
    progress: Math.max(0, Math.min(100, num(run.progress))),
    plan,
    modelRoutings,
    toolInvocations,
    startedAt: str(run.startedAt ?? run.started_at, new Date(0).toISOString()),
    updatedAt: str(run.updatedAt ?? run.updated_at, new Date(0).toISOString()),
    errors: Array.isArray(run.errors)
      ? (run.errors as Array<Record<string, unknown>>)
      : [],
    evidence: Array.isArray(run.evidence)
      ? (run.evidence as Array<Record<string, unknown>>)
      : [],
    finalOutput:
      typeof run.final_output === "string"
        ? run.final_output
        : typeof run.finalOutput === "string"
          ? run.finalOutput
          : run.final_output && typeof run.final_output === "object"
            ? (typeof (run.final_output as Record<string, unknown>).response === "string" ? (run.final_output as Record<string, unknown>).response as string : null)
            : run.finalOutput && typeof run.finalOutput === "object"
              ? (typeof (run.finalOutput as Record<string, unknown>).response === "string" ? (run.finalOutput as Record<string, unknown>).response as string : null)
              : null,
    events: Array.isArray(run.events)
      ? (run.events as Array<Record<string, unknown>>)
      : [],
  };
}

function mapEvidence(record: Record<string, unknown>): EvidenceRecord {
  const region = record.region as Partial<EvidenceRecord["region"]> | undefined;
  return {
    id: str(record.id ?? record.evidence_id),
    taskId: str(record.taskId ?? record.task_id),
    runId: str(record.runId ?? record.run_id),
    claim: str(record.claim ?? record.claim_text),
    sourceDocument: str(
      record.sourceDocument ?? record.source_document,
      "local source",
    ),
    sourceUrl:
      typeof record.sourceUrl === "string"
        ? apiUrl(record.sourceUrl)
        : typeof record.source_url === "string"
          ? apiUrl(record.source_url)
          : undefined,
    page: Math.max(1, num(record.page, 1)),
    region: {
      x: num(region?.x),
      y: num(region?.y),
      w: num(region?.w, 1),
      h: num(region?.h, 1),
    },
    extractedText: str(
      record.extractedText ??
        record.extracted_text ??
        record.claim ??
        record.claim_text,
    ),
    confidence: Math.max(0, Math.min(1, num(record.confidence))),
    validationStatus:
      record.validationStatus === "validated" ||
      record.validation_status === "validated"
        ? "validated"
        : record.validationStatus === "rejected" ||
            record.validation_status === "rejected"
          ? "rejected"
          : "pending",
    modelId:
      typeof record.modelId === "string"
        ? record.modelId
        : typeof record.model_id === "string"
          ? record.model_id
          : undefined,
    toolId:
      typeof record.toolId === "string"
        ? record.toolId
        : typeof record.tool_id === "string"
          ? record.tool_id
          : undefined,
    createdAt: str(
      record.createdAt ?? record.created_at,
      new Date(0).toISOString(),
    ),
  };
}

function mapAudit(event: Record<string, unknown>): AuditEvent {
  const decision = str(event.decision, "none");
  const status: AuditEvent["status"] =
    decision === "deny"
      ? "blocked"
      : decision === "allow"
        ? "success"
        : "pending";
  return {
    id: str(event.id ?? event.audit_event_id),
    timestamp: str(
      event.timestamp ?? event.createdAt ?? event.created_at,
      new Date(0).toISOString(),
    ),
    actor: str(event.actor ?? event.actor_id, "system"),
    taskId:
      typeof event.taskId === "string"
        ? event.taskId
        : typeof event.task_id === "string"
          ? event.task_id
          : undefined,
    modelId:
      typeof event.modelId === "string"
        ? event.modelId
        : typeof event.model_id === "string"
          ? event.model_id
          : undefined,
    toolId:
      typeof event.toolId === "string"
        ? event.toolId
        : typeof event.tool_id === "string"
          ? event.tool_id
          : undefined,
    action: str(event.action, "audit.event"),
    eventType: str(
      event.eventType ??
        event.event_type ??
        event.targetType ??
        event.target_type,
      "audit",
    ),
    result: str(event.result ?? event.reason ?? event.decision, "Recorded"),
    status,
    details:
      typeof event.details === "string"
        ? event.details
        : typeof event.reason === "string"
          ? event.reason
          : undefined,
    evidenceIds: Array.isArray(event.evidenceIds)
      ? event.evidenceIds.filter((v): v is string => typeof v === "string")
      : undefined,
  };
}

function mapModel(model: Record<string, unknown>): ModelAdapter {
  const runtime = model.runtime === "deterministic" ? "deterministic" : "local";
  const status =
    model.status === "healthy" ||
    model.status === "degraded" ||
    model.status === "offline"
      ? model.status
      : "inactive";
  return {
    id: str(model.id ?? model.model_id),
    name: str(model.name ?? model.model, "Model"),
    version: str(model.version, "—"),
    runtime,
    capabilities: Array.isArray(model.capabilities)
      ? model.capabilities.filter((v): v is string => typeof v === "string")
      : [],
    modalities: Array.isArray(model.modalities)
      ? model.modalities.filter((v): v is string => typeof v === "string")
      : undefined,
    status,
    vramGb:
      typeof model.vramGb === "number"
        ? model.vramGb
        : typeof model.vram_gb === "number"
          ? model.vram_gb
          : undefined,
    description: str(model.description),
    active: Boolean(model.active),
  };
}

function mapWorkspace(item: Record<string, unknown>): Workspace {
  return {
    id: str(item.id ?? item.workspace_id),
    name: str(item.name, "Workspace"),
    description: str(item.description),
    documentCount: num(item.documentCount ?? item.document_count),
    activeTasks: num(item.activeTasks ?? item.active_tasks),
    pendingApprovals: num(item.pendingApprovals ?? item.pending_approvals),
    deliverableCount: num(item.deliverableCount ?? item.deliverable_count),
    updatedAt: str(
      item.updatedAt ?? item.updated_at,
      new Date(0).toISOString(),
    ),
  };
}

function mapSovereignty(item: Record<string, unknown>): SovereigntyStatus {
  return {
    mode: item.mode === "active" ? "active" : "inactive",
    egressPolicy:
      item.egressPolicy === "allowlist" || item.egress_policy === "allowlist"
        ? "allowlist"
        : "deny_by_default",
    externalAllowed: num(item.externalAllowed ?? item.external_allowed),
    externalBlocked: num(item.externalBlocked ?? item.external_blocked),
    localProcessingPercent: Math.max(
      0,
      Math.min(
        100,
        num(item.localProcessingPercent ?? item.local_processing_percent),
      ),
    ),
    auditRecording: Boolean(item.auditRecording ?? item.audit_recording),
    healthyModels: num(item.healthyModels ?? item.healthy_models),
    totalModels: num(item.totalModels ?? item.total_models),
  };
}

function mapNetworkEvent(item: Record<string, unknown>): NetworkEvent {
  return {
    id: str(item.id ?? item.event_id),
    timestamp: str(
      item.timestamp ?? item.createdAt ?? item.created_at,
      new Date(0).toISOString(),
    ),
    kind:
      item.kind === "outbound_attempt" ||
      item.kind === "policy_decision" ||
      item.kind === "audit_recorded"
        ? item.kind
        : "audit_recorded",
    message: str(item.message),
    decision:
      item.decision === "allowed" || item.decision === "blocked"
        ? item.decision
        : undefined,
    reason: typeof item.reason === "string" ? item.reason : undefined,
    destination:
      typeof item.destination === "string" ? item.destination : undefined,
  };
}

function mapOverview(item: Record<string, unknown>): DashboardOverview {
  const sovereignty = (
    item.sovereignty && typeof item.sovereignty === "object"
      ? item.sovereignty
      : {}
  ) as Record<string, unknown>;
  const activity = Array.isArray(item.activity)
    ? item.activity.map((entry) => mapAudit(entry as Record<string, unknown>))
    : [];
  const currentTasks = Array.isArray(item.currentTasks ?? item.current_tasks)
    ? ((item.currentTasks ?? item.current_tasks) as unknown[])
    : [];
  const networkEvents = Array.isArray(item.networkEvents ?? item.network_events)
    ? ((item.networkEvents ?? item.network_events) as unknown[])
    : [];
  return {
    sovereignty: mapSovereignty(sovereignty),
    activeTasks: num(item.activeTasks ?? item.active_tasks),
    pendingApprovals: num(item.pendingApprovals ?? item.pending_approvals),
    recentDeliverables: num(
      item.recentDeliverables ?? item.recent_deliverables,
    ),
    recentSecurityEvents: num(
      item.recentSecurityEvents ?? item.recent_security_events,
    ),
    activity,
    currentTasks: currentTasks.map((entry) =>
      mapTask(entry as Record<string, unknown>),
    ),
    networkEvents: networkEvents.map((entry) =>
      mapNetworkEvent(entry as Record<string, unknown>),
    ),
  };
}

function mapDeliverable(item: Record<string, unknown>): Deliverable {
  const downloadUrl =
    typeof item.downloadUrl === "string"
      ? item.downloadUrl
      : typeof item.download_url === "string"
        ? item.download_url
        : undefined;
  return {
    id: str(item.id ?? item.deliverable_id),
    name: str(item.name, "Deliverable"),
    type:
      item.type === "txt" ||
      item.type === "md" ||
      item.type === "pdf" ||
      item.type === "docx" ||
      item.type === "pptx" ||
      item.type === "xlsx" ||
      item.type === "csv" ||
      item.type === "json" ||
      item.type === "code" ||
      item.type === "report" ||
      item.type === "calculation"
        ? item.type
        : "report",
    taskId: str(item.taskId ?? item.task_id),
    taskTitle: str(item.taskTitle ?? item.task_title, "Task"),
    createdAt: str(
      item.createdAt ?? item.created_at,
      new Date(0).toISOString(),
    ),
    status: statusValue(item.status),
    approvalStatus:
      item.approvalStatus === "approved" || item.approval_status === "approved"
        ? "approved"
        : item.approvalStatus === "changes_requested" ||
            item.approval_status === "changes_requested"
          ? "changes_requested"
          : item.approvalStatus === "rejected" ||
              item.approval_status === "rejected"
            ? "rejected"
            : "pending",
    evidenceCount: num(item.evidenceCount ?? item.evidence_count),
    provenanceSummary: str(item.provenanceSummary ?? item.provenance_summary),
    fileId:
      typeof item.fileId === "string"
        ? item.fileId
        : typeof item.file_id === "string"
          ? item.file_id
          : undefined,
    downloadUrl: downloadUrl ? apiUrl(downloadUrl) : undefined,
  };
}

export class ApiClient {
  readonly mode = "http" as const;

  health(): Promise<{ status: string }> {
    return httpJson<{ status: string }>("/health");
  }


  getAdminUsers(): Promise<Array<{ id: string; email: string; name: string; role: "operator" | "reviewer" | "admin"; active: boolean }>> {
    return httpJson<Array<Record<string, unknown>>>("/admin/users").then((items) => items.map((item) => ({
      id: str(item.id),
      email: str(item.email),
      name: str(item.name, "User"),
      role: str(item.role, "operator") as "operator" | "reviewer" | "admin",
      active: Boolean(item.active ?? true),
    })));
  }

  updateUserRole(userId: string, role: "operator" | "reviewer" | "admin"): Promise<{ id: string; email: string; name: string; role: "operator" | "reviewer" | "admin"; active: boolean }> {
    return httpJson<Record<string, unknown>>(`/admin/users/${encodeURIComponent(userId)}/role`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    }).then((item) => ({
      id: str(item.id),
      email: str(item.email),
      name: str(item.name, "User"),
      role: str(item.role, "operator") as "operator" | "reviewer" | "admin",
      active: Boolean(item.active ?? true),
    }));
  }

  getCurrentUser(): Promise<{ id: string; email: string; name: string; role: "operator" | "reviewer" | "admin"; active: boolean }> {
    return httpJson<Record<string, unknown>>("/auth/me").then((item) => ({
      id: str(item.id),
      email: str(item.email),
      name: str(item.name, "User"),
      role: str(item.role, "operator") as "operator" | "reviewer" | "admin",
      active: Boolean(item.active ?? true),
    }));
  }

  chatAssistant(message: string, taskId?: string): Promise<{ response: string; modelId: string; local: boolean }> {
    return httpJson<Record<string, unknown>>("/assistant/chat", {
      method: "POST",
      body: JSON.stringify({ message, task_id: taskId }),
    }).then((item) => ({
      response: str(item.response),
      modelId: str(item.modelId, "local-model"),
      local: Boolean(item.local ?? true),
    }));
  }

  getOverview(): Promise<DashboardOverview> {
    return httpJson<Record<string, unknown>>("/overview").then(mapOverview);
  }
  getWorkspaces(): Promise<Workspace[]> {
    return httpJson<Record<string, unknown>[]>("/workspaces").then((items) =>
      items.map(mapWorkspace),
    );
  }
  getWorkspace(id: string): Promise<Workspace> {
    return httpJson<Record<string, unknown>>(
      `/workspaces/${encodeURIComponent(id)}`,
    ).then(mapWorkspace);
  }
  getTasks(workspaceId?: string): Promise<TaskDefinition[]> {
    const q = workspaceId
      ? `?workspaceId=${encodeURIComponent(workspaceId)}`
      : "";
    return httpJson<Record<string, unknown>[]>(`/tasks${q}`).then((items) =>
      items.map(mapTask),
    );
  }
  getTask(id: string): Promise<TaskDefinition> {
    return httpJson<Record<string, unknown>>(
      `/tasks/${encodeURIComponent(id)}`,
    ).then(mapTask);
  }
  async uploadFile(
    file: File,
    workspaceId: string,
    createdBy: string,
  ): Promise<TaskFile> {
    if (file.size <= 0) {
      throw new ApiError("The selected file is empty.", 400, "EMPTY_FILE");
    }

    if (!workspaceId.trim()) {
      throw new ApiError(
        "A workspace must be selected before uploading a source file.",
        400,
        "WORKSPACE_REQUIRED",
      );
    }

    if (!createdBy.trim()) {
      throw new ApiError(
        "A valid local operator session is required before uploading a source file.",
        400,
        "ACTOR_REQUIRED",
      );
    }

    const body = new FormData();

    body.append("file", file, file.name);
    body.append("workspaceId", workspaceId.trim());
    body.append("createdBy", createdBy.trim());

    let response: Response;

    try {
      const headers = new Headers({
        Accept: "application/json",
      });
      const email = currentAuthEmail();
      if (email) {
        headers.set("X-User-Email", email);
      }

      response = await fetch(apiUrl("/files/upload"), {
        method: "POST",
        body,
        headers,
      });
    } catch (error) {
      throw new ApiError(
        error instanceof Error
          ? `Local API unavailable: ${error.message}`
          : "Local API unavailable.",
        0,
        "BACKEND_UNAVAILABLE",
      );
    }

    const contentType = response.headers.get("content-type") ?? "";
    const rawText = await response.text();

    let payload: unknown = null;

    if (rawText.trim()) {
      if (contentType.includes("application/json")) {
        try {
          payload = JSON.parse(rawText);
        } catch {
          payload = rawText;
        }
      } else {
        payload = rawText;
      }
    }

    if (!response.ok) {
      const errorBody =
        payload && typeof payload === "object"
          ? (payload as {
              error?: {
                message?: string;
                code?: string;
                retryable?: boolean;
              };
              detail?: string;
              message?: string;
            })
          : null;

      const serverMessage =
        errorBody?.error?.message ??
        errorBody?.detail ??
        errorBody?.message ??
        (typeof payload === "string" && payload.trim()
          ? payload.trim()
          : undefined);

      const message =
        serverMessage ||
        `Upload failed with HTTP ${response.status} ${response.statusText}`;

      throw new ApiError(message, response.status, errorBody?.error?.code);
    }

    const actual =
      payload && typeof payload === "object" && "data" in payload
        ? (
            payload as {
              data: Record<string, unknown>;
            }
          ).data
        : payload;

    if (!actual || typeof actual !== "object") {
      throw new ApiError(
        "The local API accepted the upload but returned an invalid file record.",
        502,
        "INVALID_UPLOAD_RESPONSE",
      );
    }

    return mapFile(actual as Record<string, unknown>);
  }
  createTask(input: CreateTaskInput): Promise<TaskDefinition> {
    return httpJson<Record<string, unknown>>("/tasks", {
      method: "POST",
      body: JSON.stringify(input),
    }).then(mapTask);
  }
  runTask(taskId: string): Promise<AgentState> {
    return httpJson<Record<string, unknown>>(
      `/tasks/${encodeURIComponent(taskId)}/run`,
      { method: "POST" },
    ).then(mapRun);
  }
  approveTask(taskId: string): Promise<AgentState> {
    return httpJson<Record<string, unknown>>(
      `/tasks/${encodeURIComponent(taskId)}/approve`,
      { method: "POST" },
    ).then(mapRun);
  }
  getRun(runId: string): Promise<AgentState> {
    return httpJson<Record<string, unknown>>(
      `/runs/${encodeURIComponent(runId)}`,
    ).then(mapRun);
  }
  getTaskEvents(taskId: string): Promise<Array<Record<string, unknown>>> {
    return httpJson<Array<Record<string, unknown>>>(
      `/tasks/${encodeURIComponent(taskId)}/events`,
    );
  }
  getEvidence(taskId?: string, runId?: string): Promise<EvidenceRecord[]> {
    const params = new URLSearchParams();
    if (taskId) params.set("taskId", taskId);
    if (runId) params.set("runId", runId);
    const q = params.toString() ? `?${params}` : "";
    return httpJson<Record<string, unknown>[]>(`/evidence${q}`).then((items) =>
      items.map(mapEvidence),
    );
  }
  getEvidenceById(id: string): Promise<EvidenceRecord> {
    return httpJson<Record<string, unknown>>(
      `/evidence/${encodeURIComponent(id)}`,
    ).then(mapEvidence);
  }
  async downloadFile(fileId: string): Promise<void> {
    const email = currentAuthEmail();
    const headers = new Headers({ Accept: "*/*" });
    if (email) headers.set("X-User-Email", email);
    const response = await fetch(apiUrl(`/files/${encodeURIComponent(fileId)}/download`), { headers });
    if (!response.ok) {
      const text = await response.text();
      throw new ApiError(text || `Download failed with HTTP ${response.status}`, response.status);
    }
    const blob = await response.blob();
    const disposition = response.headers.get("content-disposition") || "";
    const match = disposition.match(/filename="?([^";]+)"?/i);
    const filename = match?.[1] || "pramaan-deliverable";
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }

  getDeliverables(taskId?: string): Promise<Deliverable[]> {
    const q = taskId ? `?taskId=${encodeURIComponent(taskId)}` : "";
    return httpJson<Record<string, unknown>[]>(`/deliverables${q}`).then(
      (items) => items.map(mapDeliverable),
    );
  }
  getApprovals(): Promise<Deliverable[]> {
    return httpJson<Record<string, unknown>[]>("/approvals").then((items) =>
      items.map(mapDeliverable),
    );
  }
  decideApproval(
    input: DecideApprovalInput,
  ): Promise<Deliverable | AgentState> {
    return httpJson<Record<string, unknown>>("/approvals/decide", {
      method: "POST",
      body: JSON.stringify({ ...input, comment: input.note }),
    }).then((result) => {
      if (
        "runId" in result ||
        "run_id" in result ||
        ("progress" in result && ("taskId" in result || "task_id" in result))
      )
        return mapRun(result);
      return mapDeliverable(result);
    });
  }
  getAuditEvents(taskId?: string): Promise<AuditEvent[]> {
    const q = taskId ? `?taskId=${encodeURIComponent(taskId)}` : "";
    return httpJson<Record<string, unknown>[]>(`/audit${q}`).then((items) =>
      items.map(mapAudit),
    );
  }
  getModels(): Promise<ModelAdapter[]> {
    return httpJson<Record<string, unknown>[]>("/models").then((items) =>
      items.map(mapModel),
    );
  }
  getSovereignty(): Promise<SovereigntyStatus> {
    return httpJson<Record<string, unknown>>("/sovereignty").then(
      mapSovereignty,
    );
  }
  getNetworkEvents(): Promise<NetworkEvent[]> {
    return httpJson<Record<string, unknown>[]>("/network-events").then(
      (items) => items.map(mapNetworkEvent),
    );
  }
}

export const api = new ApiClient();
