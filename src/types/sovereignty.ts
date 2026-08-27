export type SovereigntyMode = 'active' | 'inactive'
export type EgressPolicy = 'deny_by_default' | 'allowlist'
export type NetworkEventKind =
  | 'outbound_attempt'
  | 'policy_decision'
  | 'audit_recorded'
export type NetworkDecision = 'blocked' | 'allowed'

export interface SovereigntyStatus {
  mode: SovereigntyMode
  egressPolicy: EgressPolicy
  externalAllowed: number
  externalBlocked: number
  localProcessingPercent: number
  auditRecording: boolean
  healthyModels: number
  totalModels: number
}

export interface NetworkEvent {
  id: string
  timestamp: string
  kind: NetworkEventKind
  message: string
  decision?: NetworkDecision
  reason?: string
  destination?: string
}
