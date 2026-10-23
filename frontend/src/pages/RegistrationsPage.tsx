/** Registration management: enrolment, status transitions and attendance. */
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import type { Attendee, EventItem, Registration } from '../types'
import DataTable from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { InputField, SelectField } from '../components/Form'
import Modal from '../components/Modal'
import StatusBadge from '../components/StatusBadge'
import { useToast } from '../components/Toast'
import { IconPlus } from '../components/Icons'

const STATUSES = ['Registered', 'Confirmed', 'Cancelled', 'Waitlisted']
const ATTENDANCE = ['Not Marked', 'Present', 'Absent']
const TICKET_TYPES = ['General', 'Student', 'VIP', 'Early Bird', 'Free']

const money = (value: number) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`

export default function RegistrationsPage() {
  const toast = useToast()
  const [registrations, setRegistrations] = useState<Registration[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [eventId, setEventId] = useState('')
  const [attendeeId, setAttendeeId] = useState('')
  const [status, setStatus] = useState('')
  const [attendance, setAttendance] = useState('')

  const [events, setEvents] = useState<EventItem[]>([])
  const [attendees, setAttendees] = useState<Attendee[]>([])

  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({
    attendee_id: '',
    event_id: '',
    ticket_type: 'General',
    ticket_price: '',
    registration_status: 'Registered',
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.listRegistrations({
        event_id: eventId || undefined,
        attendee_id: attendeeId || undefined,
        status: status || undefined,
        attendance_status: attendance || undefined,
      })
      setRegistrations(response.items)
      setTotal(response.total)
    } catch (err: any) {
      toast.push(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [eventId, attendeeId, status, attendance, toast])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    api.listEvents({ page_size: 100 }).then((r) => setEvents(r.items)).catch(() => undefined)
    api.listAttendees({ page_size: 200 }).then((r) => setAttendees(r.items)).catch(() => undefined)
  }, [])

  const openCreate = () => {
    setForm({ attendee_id: '', event_id: '', ticket_type: 'General', ticket_price: '', registration_status: 'Registered' })
    setFormError(null)
    setModalOpen(true)
  }

  const save = async () => {
    setSaving(true)
    setFormError(null)
    try {
      const payload: Record<string, unknown> = {
        attendee_id: Number(form.attendee_id),
        event_id: Number(form.event_id),
        ticket_type: form.ticket_type,
        registration_status: form.registration_status,
      }
      if (form.ticket_price !== '') {
        payload.ticket_price = Number(form.ticket_price)
      }
      await api.createRegistration(payload)
      toast.push('Registration created.')
      setModalOpen(false)
      load()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const changeStatus = async (registration: Registration, next: string) => {
    try {
      await api.updateRegistrationStatus(registration.registration_id, next)
      toast.push(`Registration ${registration.registration_id} → ${next}.`)
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const markAttendance = async (registration: Registration, next: string) => {
    try {
      await api.updateAttendance(registration.registration_id, next)
      toast.push(`Attendance of registration ${registration.registration_id} → ${next}.`)
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const columns: Column<Registration>[] = [
    {
      key: 'attendee_name',
      header: 'Attendee',
      render: (row) => (
        <div>
          <div className="cell-title">{row.attendee_name}</div>
          <div className="cell-sub">{row.attendee_email}</div>
        </div>
      ),
    },
    {
      key: 'event_name',
      header: 'Event',
      render: (row) => (
        <div>
          <div>{row.event_name}</div>
          <div className="cell-sub">{row.event_category} · {row.venue_name}</div>
        </div>
      ),
    },
    {
      key: 'registration_status',
      header: 'Status',
      render: (row) => <StatusBadge value={row.registration_status} />,
    },
    {
      key: 'attendance_status',
      header: 'Attendance',
      render: (row) => (
        <div className="btn-row">
          <StatusBadge value={row.attendance_status} />
          {row.registration_status !== 'Cancelled' ? (
            <>
              <button type="button" className="btn btn--ghost btn--sm" onClick={() => markAttendance(row, 'Present')}>
                Present
              </button>
              <button type="button" className="btn btn--ghost btn--sm" onClick={() => markAttendance(row, 'Absent')}>
                Absent
              </button>
            </>
          ) : null}
        </div>
      ),
    },
    {
      key: 'ticket_price',
      header: 'Ticket',
      align: 'right',
      render: (row) => (
        <div>
          <div>{row.ticket_price > 0 ? money(row.ticket_price) : 'Free'}</div>
          <div className="cell-sub">{row.ticket_type}</div>
        </div>
      ),
    },
    {
      key: 'payment_status',
      header: 'Payment',
      render: (row) => (row.payment_status ? <StatusBadge value={row.payment_status} /> : <span className="muted">—</span>),
    },
    {
      key: 'actions',
      header: 'Change status',
      render: (row) => (
        <select
          value={row.registration_status}
          onChange={(event) => changeStatus(row, event.target.value)}
          style={{ fontSize: 12, padding: '5px 8px', borderRadius: 6, border: '1px solid #cbd5e1' }}
        >
          {STATUSES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      ),
    },
  ]

  return (
    <>
      <div className="card">
        <div className="card__header">
          <div>
            <h3>Registrations</h3>
            <p>{total} registration(s) · duplicates and capacity are rejected by the backend</p>
          </div>
          <button type="button" className="btn btn--primary" onClick={openCreate}>
            <IconPlus width={15} height={15} /> Register attendee
          </button>
        </div>

        <div className="card__body">
          <div className="filters">
            <SelectField
              label="Event"
              value={eventId}
              onChange={setEventId}
              options={[
                { value: '', label: 'All events' },
                ...events.map((event) => ({ value: String(event.event_id), label: event.event_name })),
              ]}
            />
            <SelectField
              label="Attendee"
              value={attendeeId}
              onChange={setAttendeeId}
              options={[
                { value: '', label: 'All attendees' },
                ...attendees.map((attendee) => ({ value: String(attendee.attendee_id), label: attendee.full_name })),
              ]}
            />
            <SelectField
              label="Status"
              value={status}
              onChange={setStatus}
              options={[{ value: '', label: 'All statuses' }, ...STATUSES.map((item) => ({ value: item, label: item }))]}
            />
            <SelectField
              label="Attendance"
              value={attendance}
              onChange={setAttendance}
              options={[{ value: '', label: 'All attendance states' }, ...ATTENDANCE.map((item) => ({ value: item, label: item }))]}
            />
          </div>
        </div>

        <DataTable columns={columns} rows={registrations} rowKey={(row) => row.registration_id} loading={loading} />
      </div>

      <Modal
        open={modalOpen}
        title="Register an attendee"
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <button type="button" className="btn btn--ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn--primary" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Register'}
            </button>
          </>
        }
      >
        {formError ? <div className="alert alert--error" style={{ marginBottom: 14 }}>{formError}</div> : null}
        <div className="form-grid">
          <SelectField
            label="Attendee"
            value={form.attendee_id}
            onChange={(value) => setForm({ ...form, attendee_id: value })}
            options={[
              { value: '', label: 'Select an attendee' },
              ...attendees.map((attendee) => ({
                value: String(attendee.attendee_id),
                label: `${attendee.full_name} · ${attendee.organization ?? ''}`,
              })),
            ]}
          />
          <SelectField
            label="Event"
            value={form.event_id}
            onChange={(value) => setForm({ ...form, event_id: value })}
            options={[
              { value: '', label: 'Select an event' },
              ...events
                .filter((event) => event.event_status === 'Upcoming' || event.event_status === 'Ongoing')
                .map((event) => ({
                  value: String(event.event_id),
                  label: `${event.event_name} (${event.seats_available} seats left)`,
                })),
            ]}
          />
          <SelectField
            label="Ticket type"
            value={form.ticket_type}
            onChange={(value) => setForm({ ...form, ticket_type: value })}
            options={TICKET_TYPES.map((item) => ({ value: item, label: item }))}
          />
          <InputField
            label="Ticket price (₹, empty = event price)"
            type="number"
            min={0}
            step="0.01"
            value={form.ticket_price}
            onChange={(value) => setForm({ ...form, ticket_price: value })}
          />
          <SelectField
            label="Registration status"
            value={form.registration_status}
            onChange={(value) => setForm({ ...form, registration_status: value })}
            options={STATUSES.map((item) => ({ value: item, label: item }))}
            full
          />
        </div>
        <div className="alert alert--info" style={{ marginTop: 16 }}>
          The UNIQUE constraint on (attendee_id, event_id) plus the transactional capacity check guarantee that
          nobody is registered twice and that the event is never overbooked.
        </div>
      </Modal>
    </>
  )
}
