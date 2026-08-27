export type ModelRuntime = 'local' | 'deterministic'
export type ModelHealth = 'healthy' | 'degraded' | 'offline' | 'inactive'

export interface ModelAdapter {
  id: string
  name: string
  version: string
  runtime: ModelRuntime
  capabilities: string[]
  status: ModelHealth
  vramGb?: number
  description: string
  active: boolean
}
