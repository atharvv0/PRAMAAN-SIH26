import { api, type DecideApprovalInput } from './client'

export function getDeliverables(taskId?: string) {
  return api.getDeliverables(taskId)
}

export function getApprovals() {
  return api.getApprovals()
}

export function decideApproval(input: DecideApprovalInput) {
  return api.decideApproval(input)
}
