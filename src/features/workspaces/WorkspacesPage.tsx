import { Link } from 'react-router-dom'
import { DataTable, Td } from '@/components/common/DataTable'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '@/components/common/States'
import { Button } from '@/components/ui/Button'
import { useWorkspaces } from '@/hooks'
import { useWorkbenchStore } from '@/store'
import { cn, formatDateTime } from '@/lib/utils'

export function WorkspacesPage() {
  const { data, isLoading, isError, refetch } = useWorkspaces()
  const { workspaceId, setWorkspace } = useWorkbenchStore()

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Scope"
        title="Workspaces"
        description="Select a sovereign workspace to scope tasks and deliverables."
      />

      {isLoading ? <LoadingState label="Loading workspaces…" /> : null}
      {isError ? (
        <ErrorState title="Workspaces unavailable" onRetry={() => void refetch()} />
      ) : null}

      {!isLoading && !isError && data && data.length === 0 ? (
        <EmptyState title="No workspaces" />
      ) : null}

      {!isLoading && !isError && data && data.length > 0 ? (
        <DataTable
          columns={[
            'Workspace',
            'Documents',
            'Active tasks',
            'Pending approvals',
            'Deliverables',
            'Updated',
            '',
          ]}
        >
          {data.map((ws) => {
            const active = ws.id === workspaceId
            return (
              <tr
                key={ws.id}
                className={cn(
                  'hover:bg-raised/40',
                  active && 'bg-accent-soft/30',
                )}
              >
                <Td>
                  <button
                    type="button"
                    className="text-left"
                    onClick={() => setWorkspace(ws.id, ws.name)}
                  >
                    <div className="font-medium text-text hover:text-accent">
                      {ws.name}
                      {active ? (
                        <span className="ml-2 text-[10px] text-accent font-semibold">
                          ACTIVE
                        </span>
                      ) : null}
                    </div>
                    <div className="text-[11px] text-text-muted mt-0.5 line-clamp-2 max-w-md">
                      {ws.description}
                    </div>
                  </button>
                </Td>
                <Td mono>{ws.documentCount}</Td>
                <Td mono>{ws.activeTasks}</Td>
                <Td mono>{ws.pendingApprovals}</Td>
                <Td mono>{ws.deliverableCount}</Td>
                <Td mono>{formatDateTime(ws.updatedAt)}</Td>
                <Td>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      onClick={() => setWorkspace(ws.id, ws.name)}
                      disabled={active}
                    >
                      Select
                    </Button>
                    <Link
                      to="/tasks"
                      onClick={() => setWorkspace(ws.id, ws.name)}
                      className="text-[12px] text-accent hover:underline"
                    >
                      Tasks
                    </Link>
                  </div>
                </Td>
              </tr>
            )
          })}
        </DataTable>
      ) : null}
    </div>
  )
}
