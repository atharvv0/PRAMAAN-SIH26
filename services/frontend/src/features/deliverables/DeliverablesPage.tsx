import { Fragment, useState } from 'react'
import { Link } from 'react-router-dom'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Button } from '@/components/ui/Button'
import { DataTable, Td } from '@/components/common/DataTable'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '@/components/common/States'
import { useDeliverables } from '@/hooks'
import { formatDateTime } from '@/lib/utils'

export function DeliverablesPage() {
  const { data, isLoading, isError, refetch } = useDeliverables()
  const [openProvenance, setOpenProvenance] = useState<string | null>(null)

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Outputs"
        title="Deliverables"
        description="Generated artefacts with approval status and provenance."
      />

      {isLoading ? <LoadingState label="Loading deliverables…" /> : null}
      {isError ? (
        <ErrorState
          title="Deliverables unavailable"
          onRetry={() => void refetch()}
        />
      ) : null}

      {!isLoading && !isError && data && data.length === 0 ? (
        <EmptyState title="No deliverables yet" />
      ) : null}

      {!isLoading && !isError && data && data.length > 0 ? (
        <DataTable
          columns={[
            'Name',
            'Type',
            'Task',
            'Status',
            'Approval',
            'Evidence',
            'Created',
            'Actions',
          ]}
        >
          {data.map((d) => (
            <Fragment key={d.id}>
              <tr className="hover:bg-raised/40">
                <Td>
                  <div className="font-medium text-text">{d.name}</div>
                  <div className="font-mono text-[10px] text-text-muted">{d.id}</div>
                </Td>
                <Td>
                  <span className="uppercase text-[11px] text-text-muted">{d.type}</span>
                </Td>
                <Td>{d.taskTitle}</Td>
                <Td>
                  <StatusBadge status={d.status} compact />
                </Td>
                <Td>
                  <span className="text-[11px] capitalize text-text-secondary">
                    {d.approvalStatus.replace(/_/g, ' ')}
                  </span>
                </Td>
                <Td mono>{d.evidenceCount}</Td>
                <Td mono>{formatDateTime(d.createdAt)}</Td>
                <Td>
                  <div className="flex flex-wrap gap-1.5">
                    <Link to={`/evidence?taskId=${d.taskId}`}>
                      <Button size="sm">Evidence</Button>
                    </Link>
                    {d.downloadUrl ? (
                      <a href={d.downloadUrl} target="_blank" rel="noreferrer">
                        <Button size="sm">Download</Button>
                      </a>
                    ) : (
                      <Button size="sm" disabled>Download</Button>
                    )}
                    <Button
                      size="sm"
                      onClick={() =>
                        setOpenProvenance((id) => (id === d.id ? null : d.id))
                      }
                    >
                      Provenance
                    </Button>
                  </div>
                </Td>
              </tr>
              {openProvenance === d.id ? (
                <tr className="bg-surface/60">
                  <td
                    colSpan={8}
                    className="px-3 py-2.5 text-[11.5px] text-text-secondary leading-relaxed border-t border-border"
                  >
                    <span className="text-micro text-text-muted mr-2">Provenance</span>
                    {d.provenanceSummary}
                  </td>
                </tr>
              ) : null}
            </Fragment>
          ))}
        </DataTable>
      ) : null}
    </div>
  )
}
