import { api } from './client'

export function getWorkspaces() {
  return api.getWorkspaces()
}

export function getWorkspace(id: string) {
  return api.getWorkspace(id)
}
