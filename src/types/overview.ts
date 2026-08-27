import type { AuditEvent } from './audit'
import type { NetworkEvent, SovereigntyStatus } from './sovereignty'
import type { TaskDefinition } from './task'

export interface DashboardOverview {
  sovereignty: SovereigntyStatus
  activeTasks: number
  pendingApprovals: number
  recentDeliverables: number
  recentSecurityEvents: number
  activity: AuditEvent[]
  currentTasks: TaskDefinition[]
  networkEvents: NetworkEvent[]
}
