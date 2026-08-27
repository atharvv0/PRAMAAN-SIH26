import type { AgentState } from '@/types/agent'
import type { AuditEvent } from '@/types/audit'
import type { Deliverable } from '@/types/deliverable'
import type { EvidenceRecord } from '@/types/evidence'
import type { ModelAdapter } from '@/types/model'
import type { DashboardOverview } from '@/types/overview'
import type { NetworkEvent, SovereigntyStatus } from '@/types/sovereignty'
import type { TaskDefinition } from '@/types/task'
import type { Workspace } from '@/types/workspace'
import {
  mockApi,
  type CreateTaskInput,
  type DecideApprovalInput,
} from '@/mocks/adapter'

const mode = (import.meta.env.VITE_API_MODE as string | undefined) ?? 'mock'
const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''

function backendUnavailable(operation: string): never {
  throw new Error(
    `Backend not connected: ${operation} requires a live API. Set VITE_API_MODE=mock or configure VITE_API_BASE_URL.`,
  )
}

async function httpJson<T>(_path: string, _init?: RequestInit): Promise<T> {
  if (!baseUrl) {
    backendUnavailable(_path)
  }
  backendUnavailable(_path)
}

export class ApiClient {
  readonly mode: 'mock' | 'http' = mode === 'mock' ? 'mock' : 'http'

  getOverview(): Promise<DashboardOverview> {
    if (this.mode === 'mock') return mockApi.getOverview()
    return httpJson<DashboardOverview>('/overview')
  }

  getWorkspaces(): Promise<Workspace[]> {
    if (this.mode === 'mock') return mockApi.getWorkspaces()
    return httpJson<Workspace[]>('/workspaces')
  }

  getWorkspace(id: string): Promise<Workspace> {
    if (this.mode === 'mock') return mockApi.getWorkspace(id)
    return httpJson<Workspace>(`/workspaces/${id}`)
  }

  getTasks(workspaceId?: string): Promise<TaskDefinition[]> {
    if (this.mode === 'mock') return mockApi.getTasks(workspaceId)
    const q = workspaceId ? `?workspaceId=${encodeURIComponent(workspaceId)}` : ''
    return httpJson<TaskDefinition[]>(`/tasks${q}`)
  }

  getTask(id: string): Promise<TaskDefinition> {
    if (this.mode === 'mock') return mockApi.getTask(id)
    return httpJson<TaskDefinition>(`/tasks/${id}`)
  }

  createTask(input: CreateTaskInput): Promise<TaskDefinition> {
    if (this.mode === 'mock') return mockApi.createTask(input)
    return httpJson<TaskDefinition>('/tasks', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }

  getRun(runId: string): Promise<AgentState> {
    if (this.mode === 'mock') return mockApi.getRun(runId)
    return httpJson<AgentState>(`/runs/${runId}`)
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
    if (this.mode === 'mock') return mockApi.getEvidenceById(id)
    return httpJson<EvidenceRecord>(`/evidence/${id}`)
  }

  getDeliverables(taskId?: string): Promise<Deliverable[]> {
    if (this.mode === 'mock') return mockApi.getDeliverables(taskId)
    const q = taskId ? `?taskId=${encodeURIComponent(taskId)}` : ''
    return httpJson<Deliverable[]>(`/deliverables${q}`)
  }

  getApprovals(): Promise<Deliverable[]> {
    if (this.mode === 'mock') return mockApi.getApprovals()
    return httpJson<Deliverable[]>('/approvals')
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
    if (this.mode === 'mock') return mockApi.getModels()
    return httpJson<ModelAdapter[]>('/models')
  }

  getSovereignty(): Promise<SovereigntyStatus> {
    if (this.mode === 'mock') return mockApi.getSovereignty()
    return httpJson<SovereigntyStatus>('/sovereignty')
  }

  getNetworkEvents(): Promise<NetworkEvent[]> {
    if (this.mode === 'mock') return mockApi.getNetworkEvents()
    return httpJson<NetworkEvent[]>('/network-events')
  }
}

export const api = new ApiClient()

export type { CreateTaskInput, DecideApprovalInput }
