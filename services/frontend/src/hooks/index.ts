import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api";
import type { CreateTaskInput, DecideApprovalInput } from "@/api";

export const queryKeys = {
  health: ["health"] as const,
  overview: ["overview"] as const,
  workspaces: ["workspaces"] as const,
  workspace: (id: string) => ["workspaces", id] as const,
  tasks: (workspaceId?: string) => ["tasks", workspaceId ?? "all"] as const,
  task: (id: string) => ["tasks", "detail", id] as const,
  run: (id: string) => ["runs", id] as const,
  evidence: (taskId?: string, runId?: string) =>
    ["evidence", taskId ?? "all", runId ?? "all"] as const,
  evidenceItem: (id: string) => ["evidence", "item", id] as const,
  deliverables: ["deliverables"] as const,
  approvals: ["approvals"] as const,
  audit: ["audit"] as const,
  models: ["models"] as const,
  sovereignty: ["sovereignty"] as const,
  network: ["network"] as const,
};

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => api.health(),
    retry: false,
    staleTime: 5_000,
    refetchInterval: 15_000,
  });
}
export function useOverview() {
  return useQuery({
    queryKey: queryKeys.overview,
    queryFn: () => api.getOverview(),
  });
}
export function useWorkspaces() {
  return useQuery({
    queryKey: queryKeys.workspaces,
    queryFn: () => api.getWorkspaces(),
  });
}
export function useWorkspace(id: string) {
  return useQuery({
    queryKey: queryKeys.workspace(id),
    queryFn: () => api.getWorkspace(id),
    enabled: Boolean(id),
  });
}
export function useTasks(workspaceId?: string) {
  return useQuery({
    queryKey: queryKeys.tasks(workspaceId),
    queryFn: () => api.getTasks(workspaceId),
    enabled: Boolean(workspaceId),
  });
}
export function useTask(id: string) {
  return useQuery({
    queryKey: queryKeys.task(id),
    queryFn: () => api.getTask(id),
    enabled: Boolean(id),
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateTaskInput) => api.createTask(input),
    onSuccess: (task) => {
      void qc.invalidateQueries({ queryKey: ["tasks"] });
      void qc.invalidateQueries({ queryKey: queryKeys.task(task.id) });
      void qc.invalidateQueries({ queryKey: queryKeys.overview });
    },
  });
}

export function useAgentRun(runId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.run(runId ?? ""),
    queryFn: () => api.getRun(runId!),
    enabled: Boolean(runId),
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      return status === "running" || status === "queued" || status === "pending"
        ? 2_000
        : false;
    },
  });
}

function invalidateOperational(qc: ReturnType<typeof useQueryClient>) {
  void qc.invalidateQueries({ queryKey: ["tasks"] });
  void qc.invalidateQueries({ queryKey: queryKeys.overview });
  void qc.invalidateQueries({ queryKey: queryKeys.approvals });
  void qc.invalidateQueries({ queryKey: queryKeys.deliverables });
  void qc.invalidateQueries({ queryKey: queryKeys.audit });
  void qc.invalidateQueries({ queryKey: queryKeys.evidence() });
}

export function useRunTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => api.runTask(taskId),
    onSuccess: (run) => {
      invalidateOperational(qc);
      void qc.invalidateQueries({ queryKey: queryKeys.run(run.id) });
      void qc.invalidateQueries({ queryKey: queryKeys.task(run.taskId) });
    },
  });
}

export function useApproveTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => api.approveTask(taskId),
    onSuccess: (run) => {
      invalidateOperational(qc);
      void qc.invalidateQueries({ queryKey: queryKeys.run(run.id) });
      void qc.invalidateQueries({ queryKey: queryKeys.task(run.taskId) });
    },
  });
}

export function useTaskEvents(taskId: string) {
  return useQuery({
    queryKey: ["task-events", taskId],
    queryFn: () => api.getTaskEvents(taskId),
    enabled: Boolean(taskId),
    refetchInterval: 3_000,
  });
}

export function useEvidence(taskId?: string, runId?: string) {
  return useQuery({
    queryKey: queryKeys.evidence(taskId, runId),
    queryFn: () => api.getEvidence(taskId, runId),
  });
}
export function useEvidenceItem(id: string) {
  return useQuery({
    queryKey: queryKeys.evidenceItem(id),
    queryFn: () => api.getEvidenceById(id),
    enabled: Boolean(id),
  });
}
export function useDeliverables(taskId?: string) {
  return useQuery({
    queryKey: taskId
      ? [...queryKeys.deliverables, taskId]
      : queryKeys.deliverables,
    queryFn: () => api.getDeliverables(taskId),
  });
}
export function useApprovals() {
  return useQuery({
    queryKey: queryKeys.approvals,
    queryFn: () => api.getApprovals(),
  });
}
export function useDecideApproval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: DecideApprovalInput) => api.decideApproval(input),
    onSuccess: () => invalidateOperational(qc),
  });
}
export function useAuditEvents() {
  return useQuery({
    queryKey: queryKeys.audit,
    queryFn: () => api.getAuditEvents(),
  });
}
export function useModels() {
  return useQuery({
    queryKey: queryKeys.models,
    queryFn: () => api.getModels(),
  });
}
export function useSovereignty() {
  return useQuery({
    queryKey: queryKeys.sovereignty,
    queryFn: () => api.getSovereignty(),
  });
}
export function useNetworkEvents() {
  return useQuery({
    queryKey: queryKeys.network,
    queryFn: () => api.getNetworkEvents(),
    refetchInterval: (query) =>
      query.state.status === "error" ? false : 4_000,
  });
}
