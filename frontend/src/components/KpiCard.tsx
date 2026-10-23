/** KPI card for the dashboard. */
import type { ReactNode } from 'react'

interface Props {
  label: string
  value: ReactNode
  hint?: string
  icon?: ReactNode
  tone?: 'accent' | 'success' | 'warning' | 'danger' | 'purple' | 'info'
}

export default function KpiCard({ label, value, hint, icon, tone = 'accent' }: Props) {
  return (
    <div className={`kpi kpi--${tone}`}>
      {icon ? <div className="kpi__icon">{icon}</div> : null}
      <div>
        <div className="kpi__label">{label}</div>
        <div className="kpi__value">{value}</div>
        {hint ? <div className="kpi__hint">{hint}</div> : null}
      </div>
    </div>
  )
}
