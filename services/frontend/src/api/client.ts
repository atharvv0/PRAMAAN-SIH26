import type { AgentState } from '@/types/agent'
import type { AuditEvent } from '@/types/audit'
import type { Deliverable } from '@/types/deliverable'
import type { EvidenceRecord } from '@/types/evidence'
import type { ModelAdapter } from '@/types/model'
import type { DashboardOverview } from '@/types/overview'
import type { NetworkEvent, SovereigntyStatus } from '@/types/sovereignty'
import type { TaskDefinition, TaskFile } from '@/types/task'
import type { Workspace } from '@/types/workspace'
import {
  mockApi,
  type CreateTaskInput,
  type DecideApprovalInput,
} from '@/mocks/adapter'

const mode = (import.meta.env.VITE_API_MODE as string | undefined) ?? 'http'
const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '/api/v1'

export class ApiError extends Error {
  readonly status: number
  readonly code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

async function httpJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!baseUrl) {
    throw new ApiError(`Backend URL is not configured for ${path}.`, 0)
  }

  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${baseUrl.replace(/\/$/, '')}${path}`, {
    ...init,
    headers,
  })

  const text = await response.text()
  let body: unknown = null
  if (text) {
    try {
      body = JSON.parse(text)
    } catch {
      body = null
    }
  }

  if (!response.ok) {
    const errorBody = body as { error?: { message?: string; code?: string } } | null
    throw new ApiError(
      errorBody?.error?.message ?? `Request failed with HTTP ${response.status}`,
      response.status,
      errorBody?.error?.code,
    )
  }

  return body as T
}

function mapTask(task: Record<string, unknown>): TaskDefinition {
  return {
    id: String(task.id ?? task.task_id),
    title: String(task.title ?? 'PRAMAAN Task'),
    instruction: String(task.instruction ?? ''),
    workspaceId: String(task.workspaceId ?? 'ws-default'),
    workspaceName: String(task.workspaceName ?? 'PRAMAAN Sovereign Workspace'),
    status: (task.status as TaskDefinition['status']) ?? 'queued',
    progress: Number(task.progress ?? 0),
    currentStep: task.currentStep as string | undefined,
    model: task.model as string | undefined,
    createdBy: String(task.createdBy ?? 'demo.operator@local'),
    createdAt: String(task.createdAt ?? task.created_at ?? new Date().toISOString()),
    updatedAt: String(task.updatedAt ?? task.createdAt ?? new Date().toISOString()),
    elapsedMs: Number(task.elapsedMs ?? 0),
    files: (Array.isArray(task.files) ? task.files : []) as TaskFile[],
    runId: task.runId as string | undefined,
  }
}

function mapRun(run: Record<string, unknown>): AgentState {
  return {
    id: String(run.id ?? run.run_id),
    taskId: String(run.taskId ?? run.task_id),
    status: (run.status as AgentState['status']) ?? 'queued',
    currentStepId: run.currentStepId as string | undefined,
    progress: Number(run.progress ?? 0),
    plan: (Array.isArray(run.plan) ? run.plan : []) as AgentState['plan'],
    modelRoutings: (Array.isArray(run.modelRoutings) ? run.modelRoutings : []) as AgentState['modelRoutings'],
    toolInvocations: (Array.isArray(run.toolInvocations) ? run.toolInvocations : []) as AgentState['toolInvocations'],
    startedAt: String(run.startedAt ?? new Date().toISOString()),
    updatedAt: String(run.updatedAt ?? new Date().toISOString()),
  }
}

export class ApiClient {
  readonly mode: 'mock' | 'http' = mode === 'mock' ? 'mock' : 'http'

  getOverview(): Promise<DashboardOverview> {
    return this.mode === 'mock' ? mockApi.getOverview() : httpJson<DashboardOverview>('/overview')
  }

  getWorkspaces(): Promise<Workspace[]> {
    return this.mode === 'mock' ? mockApi.getWorkspaces() : httpJson<Workspace[]>('/workspaces')
  }

  getWorkspace(id: string): Promise<Workspace> {
    return this.mode === 'mock' ? mockApi.getWorkspace(id) : httpJson<Workspace>(`/workspaces/${id}`)
  }

  getTasks(workspaceId?: string): Promise<TaskDefinition[]> {
    if (this.mode === 'mock') return mockApi.getTasks(workspaceId)
    const q = workspaceId ? `?workspaceId=${encodeURIComponent(workspaceId)}` : ''
    return httpJson<Record<string, unknown>[]>(`/tasks${q}`).then((items) => items.map(mapTask))
  }

  getTask(id: string): Promise<TaskDefinition> {
    if (this.mode === 'mock') return mockApi.getTask(id)
    return httpJson<Record<string, unknown>>(`/tasks/${id}`).then(mapTask)
  }

  async uploadFile(file: File, workspaceId: string, createdBy: string) {
    if (this.mode === 'mock') {
      return { id: `file-${Date.now()}-${file.name}`, name: file.name, type: file.type || 'other', sizeBytes: file.size, status: 'queued', localProcessing: true } as TaskFile
    }
    const body = new FormData()
    body.append('file', file)
    body.append('workspaceId', workspaceId)
    body.append('createdBy', createdBy)
    const response = await fetch(`${baseUrl.replace(/\/$/, '')}/files/upload`, { method: 'POST', body, headers: { Accept: 'application/json' } })
    if (!response.ok) {
      const text = await response.text()
      throw new ApiError(text || `Upload failed with HTTP ${response.status}`, response.status)
    }
    return (await response.json()) as TaskFile
  }

  createTask(input: CreateTaskInput): Promise<TaskDefinition> {
    if (this.mode === 'mock') return mockApi.createTask(input)
    return httpJson<Record<string, unknown>>('/tasks', {
      method: 'POST',
      body: JSON.stringify(input),
    }).then(mapTask)
  }

  runTask(taskId: string) {
    if (this.mode === 'mock') return mockApi.getRun('')
    return httpJson<Record<string, unknown>>(`/tasks/${taskId}/run`, { method: 'POST' }).then(mapRun)
  }

  approveTask(taskId: string) {
    if (this.mode === 'mock') return mockApi.getRun('')
    return httpJson<Record<string, unknown>>(`/tasks/${taskId}/approve`, { method: 'POST' }).then(mapRun)
  }

  getRun(runId: string): Promise<AgentState> {
    if (this.mode === 'mock') return mockApi.getRun(runId)
    return httpJson<Record<string, unknown>>(`/runs/${runId}`).then(mapRun)
  }

  getTaskEvents(taskId: string): Promise<Array<Record<string, unknown>>> {
    if (this.mode === 'mock') return Promise.resolve([])
    return httpJson<Array<Record<string, unknown>>>(`/tasks/${taskId}/events`)
  }

  getEvidence(taskId?: string, runId?: string): Promise<EvidenceRecord[]> {
    if (this.mode === 'mock') return mockApi.getEvidence(taskId, runId)
    const params = new URLSearchParams()
    if (taskId) params.set('taskId', taskId)
    if (runId) params.set('runId', runId)
    const q = params.toString() ? `?${params}` : ''
    return httpJson<EvidenceRecord[]>(`/evidence${q}`)
  }

  getEvidenceById(id: string): Promise<EvidenceRecord> {
    return this.mode === 'mock' ? mockApi.getEvidenceById(id) : httpJson<EvidenceRecord>(`/evidence/${id}`)
  }

  getDeliverables(taskId?: string): Promise<Deliverable[]> {
    if (this.mode === 'mock') return mockApi.getDeliverables(taskId)
    const q = taskId ? `?taskId=${encodeURIComponent(taskId)}` : ''
    return httpJson<Deliverable[]>(`/deliverables${q}`)
  }

  getApprovals(): Promise<Deliverable[]> {
    return this.mode === 'mock' ? mockApi.getApprovals() : httpJson<Deliverable[]>('/approvals')
  }

  decideApproval(input: DecideApprovalInput): Promise<Deliverable> {
    if (this.mode === 'mock') return mockApi.decideApproval(input)
    return httpJson<Deliverable>('/approvals/decide', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }

  getAuditEvents(taskId?: string): Promise<AuditEvent[]> {
    if (this.mode === 'mock') return mockApi.getAuditEvents(taskId)
    const q = taskId ? `?taskId=${encodeURIComponent(taskId)}` : ''
    return httpJson<AuditEvent[]>(`/audit${q}`)
  }

  getModels(): Promise<ModelAdapter[]> {
    return this.mode === 'mock' ? mockApi.getModels() : httpJson<ModelAdapter[]>('/models')
  }

  getSovereignty(): Promise<SovereigntyStatus> {
    return this.mode === 'mock' ? mockApi.getSovereignty() : httpJson<SovereigntyStatus>('/sovereignty')
  }

  getNetworkEvents(): Promise<NetworkEvent[]> {
    return this.mode === 'mock' ? mockApi.getNetworkEvents() : httpJson<NetworkEvent[]>('/network-events')
  }
}

export const api = new ApiClient()
export type { CreateTaskInput, DecideApprovalInput }
