export type PolicyVerdict = 'allowed' | 'denied' | 'require_approval'

export interface PolicyDecision {
  id: string
  decision: PolicyVerdict
  reason: string
  policyId: string
  policyName: string
  timestamp: string
  resource?: string
  actor?: string
}
