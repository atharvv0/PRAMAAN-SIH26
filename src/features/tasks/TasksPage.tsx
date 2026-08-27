import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Button } from '@/components/ui/Button'
import { DataTable, Td } from '@/components/common/DataTable'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '@/components/common/States'
import { useTasks } from '@/hooks'
import { useWorkbenchStore } from '@/store'
import { formatClock, formatDuration } from '@/lib/utils'

export function TasksPage() {
  const workspaceId = useWorkbenchStore((s) => s.workspaceId)
  const { data, isLoading, isError, refetch } = useTasks(workspaceId)

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Workbench"
        title="Tasks"
        description="Work packages scoped to the active workspace."
        actions={
          <Link to="/tasks/new">
            <Button variant="primary" size="sm" leftIcon={<Plus className="size-3.5" />}>
              New task
            </Button>
          </Link>
        }
      />

      {isLoading ? <LoadingState label="Loading tasks…" /> : null}
      {isError ? (
        <ErrorState
          title="Tasks unavailable"
          onRetry={() => void refetch()}
        />
      ) : null}

      {!isLoading && !isError && data && data.length === 0 ? (
        <EmptyState
          title="No tasks in this workspace"
          description="Create a work package to start local agent execution."
          action={
            <Link to="/tasks/new">
              <Button size="sm" variant="primary">
                Create task
              </Button>
            </Link>
          }
        />
      ) : null}

      {!isLoading && !isError && data && data.length > 0 ? (
        <DataTable
          columns={[
            'Title',
            'Status',
            'Progress',
            'Current step',
            'Model',
            'Elapsed',
            'Updated',
            'Run',
          ]}
        >
          {data.map((task) => (
            <tr key={task.id} className="hover:bg-raised/40">
              <Td>
                <div className="font-medium text-text">{task.title}</div>
                <div className="font-mono text-[10px] text-text-muted mt-0.5">
                  {task.id}
                </div>
              </Td>
              <Td>
                <StatusBadge status={task.status} compact />
              </Td>
              <Td mono>{task.progress}%</Td>
              <Td>
                <span className="text-[11px] uppercase tracking-wide text-text-muted">
                  {task.currentStep ?? '—'}
                </span>
              </Td>
              <Td>{task.model ?? '—'}</Td>
              <Td mono>{formatDuration(task.elapsedMs)}</Td>
              <Td mono>{formatClock(task.updatedAt)}</Td>
              <Td>
                {task.runId ? (
                  <Link
                    to={`/runs/${task.runId}`}
                    className="text-accent hover:underline font-mono text-[11px]"
                  >
                    Open
                  </Link>
                ) : (
                  <span className="text-text-muted">—</span>
                )}
              </Td>
            </tr>
          ))}
        </DataTable>
      ) : null}
    </div>
  )
}
