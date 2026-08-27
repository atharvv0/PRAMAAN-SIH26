import { Link } from 'react-router-dom'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { DataTable, Td } from '@/components/common/DataTable'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '@/components/common/States'
import { useTasks } from '@/hooks'
import { formatClock, formatDuration } from '@/lib/utils'

export function RunsPage() {
  const { data, isLoading, isError, refetch } = useTasks()
  const runs = data?.filter((t) => Boolean(t.runId)) ?? []

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Execution"
        title="Runs"
        description="Agent executions linked to work packages."
      />

      {isLoading ? <LoadingState label="Loading runs…" /> : null}
      {isError ? (
        <ErrorState title="Runs unavailable" onRetry={() => void refetch()} />
      ) : null}

      {!isLoading && !isError && runs.length === 0 ? (
        <EmptyState
          title="No runs yet"
          description="Submit a task to queue a local agent run."
          action={
            <Link to="/tasks/new" className="text-xs text-accent hover:underline">
              Create task →
            </Link>
          }
        />
      ) : null}

      {!isLoading && !isError && runs.length > 0 ? (
        <DataTable
          columns={['Run ID', 'Task', 'Status', 'Progress', 'Elapsed', 'Updated', '']}
        >
          {runs.map((task) => (
            <tr key={task.runId} className="hover:bg-raised/40">
              <Td mono>{task.runId}</Td>
              <Td>
                <div className="font-medium text-text">{task.title}</div>
                <div className="text-[10px] text-text-muted">{task.workspaceName}</div>
              </Td>
              <Td>
                <StatusBadge status={task.status} compact />
              </Td>
              <Td mono>{task.progress}%</Td>
              <Td mono>{formatDuration(task.elapsedMs)}</Td>
              <Td mono>{formatClock(task.updatedAt)}</Td>
              <Td>
                <Link
                  to={`/runs/${task.runId}`}
                  className="text-accent hover:underline text-[12px]"
                >
                  Open console
                </Link>
              </Td>
            </tr>
          ))}
        </DataTable>
      ) : null}
    </div>
  )
}
