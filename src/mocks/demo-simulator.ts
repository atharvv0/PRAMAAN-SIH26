import type { StatusKind } from '@/types/status'
import { store } from './data'

const ADVANCE_ORDER: StatusKind[] = [
  'queued',
  'pending',
  'running',
  'completed',
]

/**
 * Minimal demo helper: advances the next non-terminal plan step on a run
 * so the UI can feel live without a real backend.
 */
export function advanceDemoRun(runId: string): boolean {
  const run = store.runs.find((r) => r.id === runId)
  if (!run) return false

  const step = run.plan.find(
    (s) =>
      s.status !== 'completed' &&
      s.status !== 'failed' &&
      s.status !== 'blocked' &&
      s.status !== 'external_blocked',
  )
  if (!step) return false

  if (step.status === 'approval_required') {
    return false
  }

  const idx = ADVANCE_ORDER.indexOf(step.status)
  const next: StatusKind =
    idx >= 0 && idx < ADVANCE_ORDER.length - 1
      ? ADVANCE_ORDER[idx + 1]!
      : 'completed'

  const stamp = new Date().toISOString()
  if (!step.startedAt) step.startedAt = stamp
  step.status = next
  if (next === 'completed') {
    step.completedAt = stamp
    step.durationMs = step.startedAt
      ? Math.max(0, Date.parse(stamp) - Date.parse(step.startedAt))
      : undefined
  }

  run.currentStepId = step.id
  run.updatedAt = stamp

  const completed = run.plan.filter((s) => s.status === 'completed').length
  run.progress = Math.min(99, Math.round((completed / run.plan.length) * 100))

  const task = store.tasks.find((t) => t.id === run.taskId)
  if (task) {
    task.progress = run.progress
    task.currentStep = step.label
    task.updatedAt = stamp
    if (run.status === 'queued' || run.status === 'pending') {
      run.status = 'running'
      task.status = 'running'
    }
  }

  return true
}
