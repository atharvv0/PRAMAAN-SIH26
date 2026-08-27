import { api } from './client'

export function getRun(runId: string) {
  return api.getRun(runId)
}
