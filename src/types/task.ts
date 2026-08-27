import type { StatusKind } from './status'

export type TaskFileType =
  | 'pdf'
  | 'image'
  | 'spreadsheet'
  | 'document'
  | 'other'

export interface TaskFile {
  id: string
  name: string
  type: TaskFileType
  sizeBytes: number
  status: StatusKind
  localProcessing: boolean
}

export interface TaskDefinition {
  id: string
  title: string
  instruction: string
  workspaceId: string
  workspaceName: string
  status: StatusKind
  progress: number
  currentStep?: string
  model?: string
  createdBy: string
  createdAt: string
  updatedAt: string
  elapsedMs?: number
  files: TaskFile[]
  runId?: string
}
