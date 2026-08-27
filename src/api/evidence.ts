import { api } from './client'

export function getEvidence(taskId?: string, runId?: string) {
  return api.getEvidence(taskId, runId)
}

export function getEvidenceById(id: string) {
  return api.getEvidenceById(id)
}
