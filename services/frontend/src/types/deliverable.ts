import type { StatusKind } from './status'

export type DeliverableType = 'txt' | 'md' | 'json' | 'csv' | 'docx' | 'pptx' | 'xlsx' | 'code' | 'report' | 'calculation'
export type ApprovalStatus = 'pending' | 'approved' | 'changes_requested' | 'rejected'

export interface Deliverable {
  id: string
  name: string
  type: DeliverableType
  taskId: string
  taskTitle: string
  createdAt: string
  status: StatusKind
  approvalStatus: ApprovalStatus
  evidenceCount: number
  provenanceSummary: string
  fileId?: string
  downloadUrl?: string
}
