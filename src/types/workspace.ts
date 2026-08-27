export interface Workspace {
  id: string
  name: string
  description: string
  documentCount: number
  activeTasks: number
  pendingApprovals: number
  deliverableCount: number
  updatedAt: string
}
