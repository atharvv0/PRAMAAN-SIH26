import type { LucideIcon } from 'lucide-react'
import {
  AlertTriangle,
  Ban,
  CheckCircle2,
  CircleDashed,
  Clock3,
  Loader2,
  Shield,
  ShieldAlert,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import type { StatusKind } from '@/types/status'

export interface StatusMeta {
  label: string
  description: string
  Icon: LucideIcon
  tone:
    | 'neutral'
    | 'info'
    | 'success'
    | 'warning'
    | 'danger'
    | 'blocked'
    | 'running'
    | 'sovereign'
}

export const STATUS_META: Record<StatusKind, StatusMeta> = {
  queued: {
    label: 'Queued',
    description: 'Waiting for execution capacity',
    Icon: CircleDashed,
    tone: 'neutral',
  },
  pending: {
    label: 'Pending',
    description: 'Awaiting next action',
    Icon: Clock3,
    tone: 'neutral',
  },
  running: {
    label: 'Running',
    description: 'Execution in progress',
    Icon: Loader2,
    tone: 'running',
  },
  success: {
    label: 'Success',
    description: 'Completed successfully',
    Icon: CheckCircle2,
    tone: 'success',
  },
  completed: {
    label: 'Completed',
    description: 'Workflow finished',
    Icon: CheckCircle2,
    tone: 'success',
  },
  warning: {
    label: 'Warning',
    description: 'Requires attention',
    Icon: AlertTriangle,
    tone: 'warning',
  },
  failed: {
    label: 'Failed',
    description: 'Execution failed',
    Icon: XCircle,
    tone: 'danger',
  },
  blocked: {
    label: 'Blocked',
    description: 'Blocked by policy',
    Icon: Ban,
    tone: 'blocked',
  },
  approval_required: {
    label: 'Approval Required',
    description: 'Human approval needed before finalisation',
    Icon: ShieldAlert,
    tone: 'warning',
  },
  offline: {
    label: 'Offline',
    description: 'Service unavailable',
    Icon: CircleDashed,
    tone: 'neutral',
  },
  sovereign: {
    label: 'Sovereign',
    description: 'Local sovereign mode enforced',
    Icon: ShieldCheck,
    tone: 'sovereign',
  },
  external_blocked: {
    label: 'External Request Blocked',
    description: 'Outbound network request denied by sovereignty policy',
    Icon: Shield,
    tone: 'blocked',
  },
}

export const TONE_CLASSES: Record<StatusMeta['tone'], string> = {
  neutral: 'text-text-secondary bg-raised border-border',
  info: 'text-info bg-info-soft border-info/30',
  success: 'text-success bg-success-soft border-success/30',
  warning: 'text-warning bg-warning-soft border-warning/30',
  danger: 'text-danger bg-danger-soft border-danger/30',
  blocked: 'text-blocked bg-blocked-soft border-blocked/30',
  running: 'text-running bg-running-soft border-running/30',
  sovereign: 'text-sovereign bg-accent-soft border-accent/30',
}
