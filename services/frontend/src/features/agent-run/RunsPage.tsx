import { Link } from "react-router-dom";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { DataTable, Td } from "@/components/common/DataTable";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components/common/States";
import { useTasks } from "@/hooks";
import { useWorkbenchStore } from "@/store";
import { formatClock, formatDuration } from "@/lib/utils";

export function RunsPage() {
  const workspaceId = useWorkbenchStore((s) => s.workspaceId);
  const workspaceName = useWorkbenchStore((s) => s.workspaceName);
  const query = useTasks(workspaceId || undefined);
  const runs = query.data?.filter((task) => Boolean(task.runId)) ?? [];

  if (!workspaceId)
    return (
      <div className="space-y-4">
        <PageHeader
          eyebrow="Execution"
          title="Runs"
          description="Agent executions linked to work packages in the active workspace."
          actions={
            <Link
              to="/workspaces"
              className="inline-flex h-7 items-center border border-border bg-raised px-2.5 text-[11px] font-medium text-text hover:bg-hover"
            >
              Choose workspace
            </Link>
          }
        />
        <EmptyState
          title="No workspace selected"
          description="Select a workspace to view its run history."
        />
      </div>
    );

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="Execution"
        title="Runs"
        description={`Agent executions linked to work packages in ${workspaceName}.`}
      />
      {query.isLoading ? (
        <LoadingState label="Loading execution state…" />
      ) : null}
      {query.isError ? (
        <ErrorState
          title="Runs unavailable"
          description="The local API did not return task/run state. No fallback run history is being shown."
          onRetry={() => void query.refetch()}
        />
      ) : null}
      {!query.isLoading && !query.isError && runs.length === 0 ? (
        <EmptyState
          title="No runs in this workspace"
          description="Runs appear after a task has been submitted to the execution endpoint."
          action={
            <Link
              to="/tasks/new"
              className="inline-flex h-7 items-center border border-border bg-raised px-2.5 text-[11px] font-medium text-text hover:bg-hover"
            >
              Create task
            </Link>
          }
        />
      ) : null}
      {!query.isLoading && !query.isError && runs.length > 0 ? (
        <DataTable
          columns={[
            "Run ID",
            "Task",
            "Status",
            "Progress",
            "Elapsed",
            "Updated",
            "",
          ]}
        >
          {runs.map((task) => (
            <tr key={task.runId} className="hover:bg-raised/50">
              <Td mono>{task.runId}</Td>
              <Td>
                <div className="font-medium text-text">{task.title}</div>
                <div className="mt-0.5 text-[10px] text-text-muted">
                  {task.id}
                </div>
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
                  className="text-[11px] font-medium text-accent hover:underline"
                >
                  Open console
                </Link>
              </Td>
            </tr>
          ))}
        </DataTable>
      ) : null}
    </div>
  );
}
