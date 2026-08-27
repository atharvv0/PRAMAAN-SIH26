import type { AgentState } from '@/types/agent'
import type { AuditEvent } from '@/types/audit'
import type { ApprovalStatus, Deliverable } from '@/types/deliverable'
import type { EvidenceRecord } from '@/types/evidence'
import type { ModelAdapter } from '@/types/model'
import type { DashboardOverview } from '@/types/overview'
import type { NetworkEvent, SovereigntyStatus } from '@/types/sovereignty'
import type { TaskDefinition, TaskFile } from '@/types/task'
import type { Workspace } from '@/types/workspace'
import { buildOverview, DEMO_WORKSPACE_ID, store } from './data'

function delay(ms?: number): Promise<void> {
  const wait = ms ?? 80 + Math.floor(Math.random() * 171)
  return new Promise((resolve) => setTimeout(resolve, wait))
}

function cloneTask(task: TaskDefinition): TaskDefinition {
  return {
    ...task,
    files: task.files.map((f) => ({ ...f })),
  }
}

function cloneRun(run: AgentState): AgentState {
  return {
    ...run,
    plan: run.plan.map((s) => ({ ...s })),
    modelRoutings: run.modelRoutings.map((r) => ({ ...r })),
    toolInvocations: run.toolInvocations.map((t) => ({ ...t })),
  }
}

function cloneDeliverable(d: Deliverable): Deliverable {
  return { ...d }
}

function cloneEvidence(e: EvidenceRecord): EvidenceRecord {
  return { ...e, region: { ...e.region } }
}

function nowIso(): string {
  return new Date().toISOString()
}

export type CreateTaskInput = {
  title: string
  instruction: string
  workspaceId: string
  createdBy: string
  files?: TaskFile[]
}

export type DecideApprovalInput = {
  deliverableId: string
  decision: Exclude<ApprovalStatus, 'pending'>
  actor?: string
  note?: string
}

export class MockApiAdapter {
  async getOverview(): Promise<DashboardOverview> {
    await delay()
    return buildOverview()
  }

  async getWorkspaces(): Promise<Workspace[]> {
    await delay()
    return store.workspaces.map((w) => ({ ...w }))
  }

  async getWorkspace(id: string): Promise<Workspace> {
    await delay()
    const ws = store.workspaces.find((w) => w.id === id)
    if (!ws) throw new Error(`Workspace not found: ${id}`)
    return { ...ws }
  }

  async getTasks(workspaceId?: string): Promise<TaskDefinition[]> {
    await delay()
    const list = workspaceId
      ? store.tasks.filter((t) => t.workspaceId === workspaceId)
      : store.tasks
    return list.map(cloneTask)
  }

  async getTask(id: string): Promise<TaskDefinition> {
    await delay()
    const task = store.tasks.find((t) => t.id === id)
    if (!task) throw new Error(`Task not found: ${id}`)
    return cloneTask(task)
  }

  async createTask(input: CreateTaskInput): Promise<TaskDefinition> {
    await delay()
    const workspace =
      store.workspaces.find((w) => w.id === input.workspaceId) ??
      store.workspaces.find((w) => w.id === DEMO_WORKSPACE_ID)
    if (!workspace) throw new Error('No workspace available for new task')

    const stamp = Date.now()
    const runId = `run-${stamp}`
    const taskId = `task-${stamp}`
    const createdAt = nowIso()

    const task: TaskDefinition = {
      id: taskId,
      title: input.title,
      instruction: input.instruction,
      workspaceId: workspace.id,
      workspaceName: workspace.name,
      status: 'queued',
      progress: 0,
      currentStep: 'TASK CREATED',
      createdBy: input.createdBy,
      createdAt,
      updatedAt: createdAt,
      elapsedMs: 0,
      files: (input.files ?? []).map((f) => ({ ...f })),
      runId,
    }

    const run: AgentState = {
      id: runId,
      taskId,
      status: 'queued',
      currentStepId: 'step-created',
      progress: 0,
      plan: [
        {
          id: 'step-created',
          label: 'TASK CREATED',
          status: 'completed',
          startedAt: createdAt,
          completedAt: createdAt,
          durationMs: 0,
          details: 'Task accepted into sovereign queue.',
        },
        {
          id: 'step-planning',
          label: 'PLANNING',
          status: 'queued',
        },
      ],
      modelRoutings: [],
      toolInvocations: [],
      startedAt: createdAt,
      updatedAt: createdAt,
    }

    store.tasks = [task, ...store.tasks]
    store.runs = [run, ...store.runs]
    workspace.activeTasks += 1
    workspace.updatedAt = createdAt

    store.auditEvents = [
      {
        id: `aud-${stamp}`,
        timestamp: createdAt,
        actor: input.createdBy,
        taskId,
        action: 'task.created',
        eventType: 'task_lifecycle',
        result: `Task "${input.title}" created`,
        status: 'success',
      },
      ...store.auditEvents,
    ]

    return cloneTask(task)
  }

  async getRun(runId: string): Promise<AgentState> {
    await delay()
    const run = store.runs.find((r) => r.id === runId)
    if (!run) throw new Error(`Run not found: ${runId}`)
    return cloneRun(run)
  }

  async getEvidence(taskId?: string, runId?: string): Promise<EvidenceRecord[]> {
    await delay()
    let list = store.evidence
    if (taskId) list = list.filter((e) => e.taskId === taskId)
    if (runId) list = list.filter((e) => e.runId === runId)
    return list.map(cloneEvidence)
  }

  async getEvidenceById(id: string): Promise<EvidenceRecord> {
    await delay()
    const record = store.evidence.find((e) => e.id === id)
    if (!record) throw new Error(`Evidence not found: ${id}`)
    return cloneEvidence(record)
  }

  async getDeliverables(taskId?: string): Promise<Deliverable[]> {
    await delay()
    const list = taskId
      ? store.deliverables.filter((d) => d.taskId === taskId)
      : store.deliverables
    return list.map(cloneDeliverable)
  }

  async getApprovals(): Promise<Deliverable[]> {
    await delay()
    return store.deliverables
      .filter((d) => d.approvalStatus === 'pending')
      .map(cloneDeliverable)
  }

  async decideApproval(input: DecideApprovalInput): Promise<Deliverable> {
    await delay()
    const deliverable = store.deliverables.find((d) => d.id === input.deliverableId)
    if (!deliverable) throw new Error(`Deliverable not found: ${input.deliverableId}`)

    deliverable.approvalStatus = input.decision
    deliverable.status =
      input.decision === 'approved'
        ? 'completed'
        : input.decision === 'changes_requested'
          ? 'warning'
          : 'failed'
    deliverable.createdAt = deliverable.createdAt

    const stamp = nowIso()
    const actor = input.actor ?? 'insp.authority@mrpl.local'

    store.auditEvents = [
      {
        id: `aud-approval-${Date.now()}`,
        timestamp: stamp,
        actor,
        taskId: deliverable.taskId,
        action: 'approval.decided',
        eventType: 'approval',
        result: `${deliverable.name} marked ${input.decision}`,
        status:
          input.decision === 'approved'
            ? 'success'
            : input.decision === 'changes_requested'
              ? 'warning'
              : 'failed',
        details: input.note,
      },
      ...store.auditEvents,
    ]

    const ws = store.workspaces.find((w) =>
      store.tasks.some((t) => t.id === deliverable.taskId && t.workspaceId === w.id),
    )
    if (ws) {
      ws.pendingApprovals = store.deliverables.filter(
        (d) =>
          d.approvalStatus === 'pending' &&
          store.tasks.some((t) => t.id === d.taskId && t.workspaceId === ws.id),
      ).length
      ws.updatedAt = stamp
    }

    const task = store.tasks.find((t) => t.id === deliverable.taskId)
    if (task && input.decision === 'approved') {
      const stillPending = store.deliverables.some(
        (d) => d.taskId === task.id && d.approvalStatus === 'pending',
      )
      if (!stillPending) {
        task.status = 'completed'
        task.progress = 100
        task.currentStep = 'AUDIT COMPLETE'
        task.updatedAt = stamp
      }
    }

    return cloneDeliverable(deliverable)
  }

  async getAuditEvents(taskId?: string): Promise<AuditEvent[]> {
    await delay()
    const list = taskId
      ? store.auditEvents.filter((e) => e.taskId === taskId)
      : store.auditEvents
    return list.map((e) => ({
      ...e,
      policyDecision: e.policyDecision ? { ...e.policyDecision } : undefined,
      evidenceIds: e.evidenceIds ? [...e.evidenceIds] : undefined,
    }))
  }

  async getModels(): Promise<ModelAdapter[]> {
    await delay()
    return store.models.map((m) => ({
      ...m,
      capabilities: [...m.capabilities],
    }))
  }

  async getSovereignty(): Promise<SovereigntyStatus> {
    await delay()
    return { ...store.sovereignty }
  }

  async getNetworkEvents(): Promise<NetworkEvent[]> {
    await delay()
    return store.networkEvents.map((e) => ({ ...e }))
  }
}

export const mockApi = new MockApiAdapter()
