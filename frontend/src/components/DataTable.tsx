/** Generic, responsive data table. */
import type { ReactNode } from 'react'

export interface Column<T> {
  key: string
  header: string
  render?: (row: T) => ReactNode
  align?: 'left' | 'right'
  width?: string
}

interface Props<T> {
  columns: Column<T>[]
  rows: T[]
  rowKey: (row: T) => string | number
  emptyMessage?: string
  loading?: boolean
  onRowClick?: (row: T) => void
}

export default function DataTable<T>({
  columns,
  rows,
  rowKey,
  emptyMessage = 'No records found.',
  loading = false,
  onRowClick,
}: Props<T>) {
  if (loading) {
    return <div className="loading-row"><span className="spinner" /> Loading…</div>
  }

  if (!rows.length) {
    return (
      <div className="empty">
        <strong>Nothing to show</strong>
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="table-wrap">
      <table className="data">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={column.align === 'right' ? 'num' : undefined} style={column.width ? { width: column.width } : undefined}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={rowKey(row)}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              style={onRowClick ? { cursor: 'pointer' } : undefined}
            >
              {columns.map((column) => (
                <td key={column.key} className={column.align === 'right' ? 'num' : undefined}>
                  {column.render ? column.render(row) : String((row as any)[column.key] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
