import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export function DataTable({
  columns,
  children,
  className,
}: {
  columns: string[]
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn('overflow-auto border border-border bg-panel', className)}>
      <table className="w-full text-left text-[12.5px]">
        <thead className="bg-surface sticky top-0 z-10">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="px-3 py-2 text-micro text-text-muted font-semibold border-b border-border whitespace-nowrap"
              >
                {col || '\u00a0'}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-panel">{children}</tbody>
      </table>
    </div>
  )
}

export function Td({
  children,
  className,
  mono,
}: {
  children: ReactNode
  className?: string
  mono?: boolean
}) {
  return (
    <td
      className={cn(
        'px-3 py-2 align-middle text-text-secondary',
        mono && 'font-mono text-[11px] text-text',
        className,
      )}
    >
      {children}
    </td>
  )
}
