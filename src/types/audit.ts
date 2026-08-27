import type { PolicyDecision } from './policy'
import type { StatusKind } from './status'

export interface AuditEvent {
  id: string
  timestamp: string
  actor: string
  taskId?: string
  modelId?: string
  toolId?: string
  action: string
  eventType: string
  policyDecision?: PolicyDecision
  evidenceIds?: string[]
  result: string
  status: StatusKind
  details?: string
}
