import { DataTable, Td } from '@/components/common/DataTable'
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '@/components/common/States'
import { ModelBadge } from '@/components/common/Indicators'
import { useModels } from '@/hooks'
import { cn } from '@/lib/utils'
import type { ModelHealth } from '@/types/model'

export function ModelsPage() {
  const { data, isLoading, isError, refetch } = useModels()

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Registry"
        title="Model registry"
        description="Local and deterministic adapters available to sovereign runs."
      />

      {isLoading ? <LoadingState label="Loading model registry…" /> : null}
      {isError ? (
        <ErrorState title="Models unavailable" onRetry={() => void refetch()} />
      ) : null}

      {!isLoading && !isError && data && data.length === 0 ? (
        <EmptyState title="No models registered" />
      ) : null}

      {!isLoading && !isError && data && data.length > 0 ? (
        <DataTable
          columns={[
            'Model',
            'Version',
            'Runtime',
            'Health',
            'VRAM',
            'Active',
            'Capabilities',
          ]}
        >
          {data.map((m) => (
            <tr key={m.id} className="hover:bg-raised/40">
              <Td>
                <div className="space-y-1">
                  <ModelBadge name={m.name} local={m.runtime === 'local'} />
                  <div className="font-mono text-[10px] text-text-muted">{m.id}</div>
                  <p className="text-[11px] text-text-muted leading-snug max-w-md">
                    {m.description}
                  </p>
                </div>
              </Td>
              <Td mono>{m.version}</Td>
              <Td>
                <span className="text-[11px] uppercase text-text-secondary">
                  {m.runtime}
                </span>
              </Td>
              <Td>
                <HealthChip status={m.status} />
              </Td>
              <Td mono>{m.vramGb != null ? `${m.vramGb} GB` : '—'}</Td>
              <Td>
                <span
                  className={cn(
                    'text-[11px] font-medium',
                    m.active ? 'text-success' : 'text-text-muted',
                  )}
                >
                  {m.active ? 'Yes' : 'No'}
                </span>
              </Td>
              <Td>
                <div className="flex flex-wrap gap-1 max-w-xs">
                  {m.capabilities.map((c) => (
                    <span
                      key={c}
                      className="text-[10px] border border-border bg-raised px-1.5 py-0.5 text-text-secondary"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </Td>
            </tr>
          ))}
        </DataTable>
      ) : null}
    </div>
  )
}

function HealthChip({ status }: { status: ModelHealth }) {
  const tone =
    status === 'healthy'
      ? 'text-success border-success/30 bg-success-soft'
      : status === 'degraded'
        ? 'text-warning border-warning/30 bg-warning-soft'
        : status === 'offline'
          ? 'text-danger border-danger/30 bg-danger-soft'
          : 'text-text-muted border-border bg-raised'

  return (
    <span
      className={cn(
        'text-[10px] px-1.5 py-0.5 border font-medium capitalize',
        tone,
      )}
    >
      {status}
    </span>
  )
}
