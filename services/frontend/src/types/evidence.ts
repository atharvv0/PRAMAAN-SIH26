export type ValidationStatus = 'validated' | 'pending' | 'rejected'

export interface EvidenceRegion {
  x: number
  y: number
  w: number
  h: number
}

export interface EvidenceRecord {
  id: string
  taskId: string
  runId: string
  claim: string
  sourceDocument: string
  sourceUrl?: string
  page: number
  region: EvidenceRegion
  extractedText: string
  confidence: number
  validationStatus: ValidationStatus
  modelId?: string
  toolId?: string
  createdAt: string
}
