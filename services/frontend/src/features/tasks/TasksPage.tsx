import { Link } from 'react-router-dom'
import { Play, Plus } from 'lucide-react'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Button } from '@/components/ui/Button'
import { DataTable, Td } from '@/components/common/DataTable'
import { EmptyState, ErrorState, LoadingState, PageHeader } from '@/components/common/States'
import { useRunTask, useTasks } from '@/hooks'
import { useWorkbenchStore } from '@/store'
import { formatClock, formatDuration } from '@/lib/utils'

export function TasksPage() {
  const workspaceId = useWorkbenchStore((s) => s.workspaceId)
  const workspaceName = useWorkbenchStore((s) => s.workspaceName)
  const runTask = useRunTask()
  const query = useTasks(workspaceId || undefined)

  if (!workspaceId) return <div className="space-y-4"><PageHeader eyebrow="Workbench" title="Tasks" description="Work packages in the active sovereign workspace." actions={<Link to="/workspaces" className="inline-flex h-7 items-center border border-border bg-raised px-2.5 text-[11px] font-medium text-text hover:bg-hover">Choose workspace</Link>} /><EmptyState title="No workspace selected" description="Select a workspace before loading task state. PRAMAAN does not invent a default workspace." /></div>

  return <div className="space-y-4"><PageHeader eyebrow="Workbench" title="Tasks" description={`Work packages scoped to ${workspaceName}.`} actions={<Link to="/tasks/new" className="inline-flex h-8 items-center gap-1.5 border border-accent bg-accent px-3 text-[11px] font-semibold text-canvas hover:brightness-110"><Plus className="size-3.5" aria-hidden />New task</Link>} />
    {query.isLoading ? <LoadingState label="Loading live task state…" /> : null}
    {query.isError ? <ErrorState title="Tasks unavailable" description="The local API did not return task state. No fallback dataset is being shown." onRetry={() => void query.refetch()} /> : null}
    {!query.isLoading && !query.isError && query.data?.length === 0 ? <EmptyState title="No tasks in this workspace" description="Create a work package to begin a local agent run." action={<Link to="/tasks/new" className="inline-flex h-7 items-center border border-accent bg-accent px-2.5 text-[11px] font-semibold text-canvas">Create task</Link>} /> : null}
    {!query.isLoading && !query.isError && query.data && query.data.length > 0 ? <DataTable columns={['Task', 'Status', 'Progress', 'Current step', 'Model', 'Elapsed', 'Updated', 'Action']}>
      {query.data.map((task) => <tr key={task.id} className="hover:bg-raised/50"><Td><div className="font-medium text-text">{task.title}</div><div className="mt-0.5 font-mono text-[10px] text-text-muted">{task.id}</div></Td><Td><StatusBadge status={task.status} compact /></Td><Td mono><div className="flex min-w-[90px] items-center gap-2"><div className="h-1.5 flex-1 bg-canvas"><div className="h-full bg-running" style={{ width: `${task.progress}%` }} /></div><span>{task.progress}%</span></div></Td><Td>{task.currentStep ?? '—'}</Td><Td>{task.model ?? '—'}</Td><Td mono>{formatDuration(task.elapsedMs)}</Td><Td mono>{formatClock(task.updatedAt)}</Td><Td>{task.runId ? <Link to={`/runs/${task.runId}`} className="text-[11px] font-medium text-accent hover:underline">Open run</Link> : <Button size="sm" disabled={runTask.isPending} onClick={() => void runTask.mutateAsync(task.id)} leftIcon={<Play className="size-3" />}>{runTask.isPending ? 'Starting…' : 'Run'}</Button>}</Td></tr>)}
    </DataTable> : null}
  </div>
}
