import type { StatusKind } from './status'

export type ToolPermission = 'allowed' | 'blocked'

export interface AgentStep {
  id: string
  label: string
  status: StatusKind
  startedAt?: string
  completedAt?: string
  durationMs?: number
  toolId?: string
  modelId?: string
  details?: string
  evidenceCount?: number
  warning?: string
  error?: string
}

export interface ModelRouting {
  stepId: string
  taskLabel: string
  modelId: string
  modelName: string
  reason: string
  local: boolean
  status: StatusKind
}

export interface ToolInvocation {
  id: string
  tool: string
  status: StatusKind
  permission: ToolPermission
  reason: string
  timestamp: string
  durationMs?: number
  inputSummary?: string
  outputSummary?: string
}

export interface AgentState {
  id: string
  taskId: string
  status: StatusKind
  currentStepId?: string
  progress: number
  plan: AgentStep[]
  modelRoutings: ModelRouting[]
  toolInvocations: ToolInvocation[]
  startedAt: string
  updatedAt: string
  errors?: Array<Record<string, unknown>>
  evidence?: Array<Record<string, unknown>>
  finalOutput?: string | null
  events?: Array<Record<string, unknown>>
}
