import { api } from './client'

export function getAuditEvents(taskId?: string) {
  return api.getAuditEvents(taskId)
}
