import type { StatusKind } from '@/types/status'
import { STATUS_META, TONE_CLASSES } from '@/lib/status'
import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: StatusKind
  className?: string
  showIcon?: boolean
  compact?: boolean
}

export function StatusBadge({
  status,
  className,
  showIcon = true,
  compact = false,
}: StatusBadgeProps) {
  const meta = STATUS_META[status]
  const Icon = meta.Icon
  return (
    <span
      title={meta.description}
      className={cn(
        'inline-flex items-center gap-1 border font-medium whitespace-nowrap',
        compact ? 'px-1.5 py-0.5 text-[10px] leading-none' : 'px-2 py-0.5 text-[11px]',
        TONE_CLASSES[meta.tone],
        className,
      )}
    >
      {showIcon ? (
        <Icon
          className={cn(
            'shrink-0',
            compact ? 'size-2.5' : 'size-3',
            status === 'running' && 'animate-spin',
          )}
          aria-hidden
        />
      ) : null}
      <span>{meta.label}</span>
    </span>
  )
}
