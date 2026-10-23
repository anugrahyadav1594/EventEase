/** Dashboard: every number is calculated by the database. */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import type { Dashboard } from '../types'
import { BarCard, DonutCard } from '../components/Charts'
import { IconCard, IconChart, IconCheck, IconClock, IconMoney, IconTicket, IconUsers } from '../components/Icons'
import KpiCard from '../components/KpiCard'
import StatusBadge from '../components/StatusBadge'

const money = (value: number) =>
  `₹${Number(value ?? 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

const shortDate = (value?: string | null) => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

const timeLabel = (value?: string | null) => (value ? value.slice(0, 5) : '—')

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .dashboard()
      .then(setData)
      .catch((err) => setError(err.message))
  }, [])

  if (error) {
    return <div className="alert alert--error">{error}</div>
  }

  if (!data) {
    return (
      <div className="loading-row">
        <span className="spinner" /> Loading dashboard…
      </div>
    )
  }

  const m = data.metrics

  return (
    <div className="stack" style={{ gap: 20 }}>
      <section className="kpi-grid">
        <KpiCard
          label="Total events"
          value={m.total_events}
          hint={`${m.upcoming_events} upcoming · ${m.ongoing_events} ongoing`}
          icon={<IconChart />}
        />
        <KpiCard
          label="Completed events"
          value={m.completed_events}
          hint={`${m.cancelled_events} cancelled`}
          tone="success"
          icon={<IconCheck />}
        />
        <KpiCard
          label="Attendees"
          value={m.total_attendees}
          hint="unique participants"
          tone="info"
          icon={<IconUsers />}
        />
        <KpiCard
          label="Registrations"
          value={m.total_registrations}
          hint={`${m.confirmed_registrations} confirmed · ${m.waitlisted_registrations} waitlisted`}
          icon={<IconTicket />}
        />
        <KpiCard
          label="Revenue collected"
          value={money(m.total_revenue)}
          hint={`${money(m.pending_amount)} pending · ${money(m.refunded_amount)} refunded`}
          tone="success"
          icon={<IconMoney />}
        />
        <KpiCard
          label="Average attendance"
          value={`${m.average_attendance_rate}%`}
          hint={`${m.present_count} present · ${m.absent_count} absent`}
          tone="purple"
          icon={<IconClock />}
        />
        <KpiCard
          label="Payment records"
          value={m.payment_records}
          hint="completed + pending + refunded"
          tone="warning"
          icon={<IconCard />}
        />
        <KpiCard
          label="Venues"
          value={m.total_venues}
          hint={`${m.total_organizers} organizers`}
          tone="info"
          icon={<IconUsers />}
        />
      </section>

      <section className="grid-main">
        <div className="card">
          <div className="card__header">
            <div>
              <h3>Registrations by event</h3>
              <p>GROUP BY + COUNT over the registrations table</p>
            </div>
            <Link className="btn btn--ghost btn--sm" to="/events">
              Open events
            </Link>
          </div>
          <div className="card__body">
            <BarCard
              data={data.charts.registrations_by_event}
              xKey="event_name"
              bars={[{ key: 'total_registrations', color: '#2563eb', name: 'Registrations' }]}
            />
          </div>
        </div>

        <div className="card">
          <div className="card__header">
            <div>
              <h3>Revenue by category</h3>
              <p>Only completed payments are counted</p>
            </div>
          </div>
          <div className="card__body">
            <DonutCard
              data={data.charts.revenue_by_category}
              nameKey="event_category"
              valueKey="revenue"
              valueFormatter={money}
            />
          </div>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="card__header">
            <div>
              <h3>Attendance by event</h3>
              <p>Present / absent split of the marked registrations</p>
            </div>
          </div>
          <div className="card__body">
            <BarCard
              data={data.charts.attendance_by_event}
              xKey="event_name"
              stacked
              bars={[
                { key: 'present_count', color: '#16a34a', name: 'Present' },
                { key: 'absent_count', color: '#dc2626', name: 'Absent' },
              ]}
            />
          </div>
        </div>

        <div className="card">
          <div className="card__header">
            <div>
              <h3>Venue utilisation</h3>
              <p>Registrations compared with the seats offered</p>
            </div>
          </div>
          <div className="card__body">
            <BarCard
              data={data.charts.venue_utilization}
              xKey="venue_name"
              bars={[{ key: 'utilization_percent', color: '#8b5cf6', name: 'Utilisation %' }]}
              valueFormatter={(value) => `${value}%`}
            />
          </div>
        </div>
      </section>

      <section className="grid-main">
        <div className="card">
          <div className="card__header">
            <div>
              <h3>Upcoming schedule</h3>
              <p>Read from the view v_upcoming_events</p>
            </div>
          </div>
          <div className="card__body card__body--flush">
            <div className="table-wrap">
              <table className="data">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Venue</th>
                    <th className="num">Seats</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.upcoming_schedule.map((item: any) => (
                    <tr key={item.event_id}>
                      <td>
                        <div className="cell-title">{item.event_name}</div>
                        <div className="cell-sub">{item.event_category} · {item.organizer_name}</div>
                      </td>
                      <td className="nowrap">{shortDate(item.event_date)}</td>
                      <td className="nowrap mono">
                        {timeLabel(item.start_time)} – {timeLabel(item.end_time)}
                      </td>
                      <td>{item.venue_name}</td>
                      <td className="num">
                        {item.active_registrations}/{item.capacity}
                      </td>
                      <td>
                        <StatusBadge value={item.event_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card__header">
            <div>
              <h3>Most popular events</h3>
              <p>Top five by registration count</p>
            </div>
          </div>
          <div className="card__body card__body--flush">
            <div className="table-wrap">
              <table className="data">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th className="num">Registrations</th>
                    <th className="num">Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {data.popular_events.map((item: any) => (
                    <tr key={item.event_id}>
                      <td>
                        <div className="cell-title">{item.event_name}</div>
                        <div className="cell-sub">{item.event_category}</div>
                      </td>
                      <td className="num strong">{item.total_registrations}</td>
                      <td className="num">{money(item.revenue)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
