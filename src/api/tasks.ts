import { api, type CreateTaskInput } from './client'

export function getTasks(workspaceId?: string) {
  return api.getTasks(workspaceId)
}

export function getTask(id: string) {
  return api.getTask(id)
}

export function createTask(input: CreateTaskInput) {
  return api.createTask(input)
}
