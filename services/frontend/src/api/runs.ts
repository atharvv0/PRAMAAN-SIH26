import { api } from './client'

export function getRun(runId: string) {
  return api.getRun(runId)
}

export function getTaskEvents(taskId: string) {
  return api.getTaskEvents(taskId)
}
