/** Coloured status pill used for events, registrations and payments. */
import type { ReactNode } from 'react'

type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'accent'

const TONES: Record<string, Tone> = {
  // events
  Upcoming: 'accent',
  Ongoing: 'info',
  Completed: 'success',
  Cancelled: 'danger',
  // venues
  Available: 'success',
  Unavailable: 'danger',
  Maintenance: 'warning',
  // registrations
  Registered: 'accent',
  Confirmed: 'success',
  Waitlisted: 'warning',
  // attendance
  Present: 'success',
  Absent: 'danger',
  'Not Marked': 'neutral',
  // payments
  Pending: 'warning',
  Refunded: 'purple',
}

interface Props {
  value: string | null | undefined
  tone?: Tone
  children?: ReactNode
}

export default function StatusBadge({ value, tone, children }: Props) {
  const label = value ?? '—'
  const resolved = tone ?? TONES[label] ?? 'neutral'
  return (
    <span className={`badge badge--${resolved}`}>
      <span className="badge-dot" />
      {children ?? label}
    </span>
  )
}
