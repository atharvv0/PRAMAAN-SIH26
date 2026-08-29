import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api'
import type { CreateTaskInput, DecideApprovalInput } from '@/mocks/adapter'

export const queryKeys = {
  overview: ['overview'] as const,
  workspaces: ['workspaces'] as const,
  workspace: (id: string) => ['workspaces', id] as const,
  tasks: (workspaceId?: string) => ['tasks', workspaceId ?? 'all'] as const,
  task: (id: string) => ['tasks', 'detail', id] as const,
  run: (id: string) => ['runs', id] as const,
  evidence: (taskId?: string, runId?: string) =>
    ['evidence', taskId ?? 'all', runId ?? 'all'] as const,
  evidenceItem: (id: string) => ['evidence', 'item', id] as const,
  deliverables: ['deliverables'] as const,
  approvals: ['approvals'] as const,
  audit: ['audit'] as const,
  models: ['models'] as const,
  sovereignty: ['sovereignty'] as const,
  network: ['network'] as const,
}

export function useOverview() {
  return useQuery({ queryKey: queryKeys.overview, queryFn: () => api.getOverview() })
}

export function useWorkspaces() {
  return useQuery({ queryKey: queryKeys.workspaces, queryFn: () => api.getWorkspaces() })
}

export function useWorkspace(id: string) {
  return useQuery({
    queryKey: queryKeys.workspace(id),
    queryFn: () => api.getWorkspace(id),
    enabled: Boolean(id),
  })
}

export function useTasks(workspaceId?: string) {
  return useQuery({
    queryKey: queryKeys.tasks(workspaceId),
    queryFn: () => api.getTasks(workspaceId),
  })
}

export function useTask(id: string) {
  return useQuery({
    queryKey: queryKeys.task(id),
    queryFn: () => api.getTask(id),
    enabled: Boolean(id),
  })
}

export function useCreateTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: CreateTaskInput) => api.createTask(input),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['tasks'] })
      void qc.invalidateQueries({ queryKey: queryKeys.overview })
    },
  })
}

export function useAgentRun(runId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.run(runId ?? ''),
    queryFn: () => api.getRun(runId!),
    enabled: Boolean(runId),
    refetchInterval: (q) => {
      const status = q.state.data?.status
      return status === 'running' || status === 'queued' ? 2000 : false
    },
  })
}


export function useRunTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (taskId: string) => api.runTask(taskId),
    onSuccess: (run) => {
      void qc.invalidateQueries({ queryKey: queryKeys.tasks() })
      void qc.invalidateQueries({ queryKey: queryKeys.task(run.taskId) })
      void qc.invalidateQueries({ queryKey: queryKeys.run(run.id) })
    },
  })
}

export function useApproveTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (taskId: string) => api.approveTask(taskId),
    onSuccess: (run) => {
      void qc.invalidateQueries({ queryKey: queryKeys.approvals })
      void qc.invalidateQueries({ queryKey: queryKeys.deliverables })
      void qc.invalidateQueries({ queryKey: queryKeys.run(run.id) })
      void qc.invalidateQueries({ queryKey: queryKeys.task(run.taskId) })
    },
  })
}

export function useEvidence(taskId?: string, runId?: string) {
  return useQuery({
    queryKey: queryKeys.evidence(taskId, runId),
    queryFn: () => api.getEvidence(taskId, runId),
  })
}

export function useEvidenceItem(id: string) {
  return useQuery({
    queryKey: queryKeys.evidenceItem(id),
    queryFn: () => api.getEvidenceById(id),
    enabled: Boolean(id),
  })
}

export function useDeliverables() {
  return useQuery({
    queryKey: queryKeys.deliverables,
    queryFn: () => api.getDeliverables(),
  })
}

export function useApprovals() {
  return useQuery({
    queryKey: queryKeys.approvals,
    queryFn: () => api.getApprovals(),
  })
}

export function useDecideApproval() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: DecideApprovalInput) => api.decideApproval(input),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.approvals })
      void qc.invalidateQueries({ queryKey: queryKeys.deliverables })
      void qc.invalidateQueries({ queryKey: queryKeys.overview })
    },
  })
}

export function useAuditEvents() {
  return useQuery({ queryKey: queryKeys.audit, queryFn: () => api.getAuditEvents() })
}

export function useModels() {
  return useQuery({ queryKey: queryKeys.models, queryFn: () => api.getModels() })
}

export function useSovereignty() {
  return useQuery({
    queryKey: queryKeys.sovereignty,
    queryFn: () => api.getSovereignty(),
  })
}

export function useNetworkEvents() {
  return useQuery({
    queryKey: queryKeys.network,
    queryFn: () => api.getNetworkEvents(),
    refetchInterval: 4000,
  })
}
