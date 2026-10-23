/** Event management: search, filters, pagination and full CRUD. */
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import type { EventItem, Organizer, Venue } from '../types'
import DataTable from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { InputField, SelectField, TextAreaField } from '../components/Form'
import Modal from '../components/Modal'
import StatusBadge from '../components/StatusBadge'
import { useToast } from '../components/Toast'
import { IconEdit, IconPlus, IconRefresh, IconTrash } from '../components/Icons'

const CATEGORIES = ['Technical', 'Cultural', 'Sports', 'Business', 'Workshop']
const STATUSES = ['Upcoming', 'Ongoing', 'Completed', 'Cancelled']

const emptyForm = {
  event_name: '',
  description: '',
  event_category: 'Technical',
  organizer_id: '',
  venue_id: '',
  event_date: '',
  start_time: '10:00',
  end_time: '12:00',
  capacity: '50',
  ticket_price: '0',
  event_status: 'Upcoming',
}

const money = (value: number) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`

export default function EventsPage() {
  const toast = useToast()
  const [events, setEvents] = useState<EventItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [status, setStatus] = useState('')
  const [organizerId, setOrganizerId] = useState('')
  const [venueId, setVenueId] = useState('')

  const [organizers, setOrganizers] = useState<Organizer[]>([])
  const [venues, setVenues] = useState<Venue[]>([])

  const [form, setForm] = useState({ ...emptyForm })
  const [editingId, setEditingId] = useState<number | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [detail, setDetail] = useState<EventItem | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.listEvents({
        search: search || undefined,
        category: category || undefined,
        status: status || undefined,
        organizer_id: organizerId || undefined,
        venue_id: venueId || undefined,
        page,
        page_size: pageSize,
      })
      setEvents(response.items)
      setTotal(response.total)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [search, category, status, organizerId, venueId, page, pageSize])

  useEffect(() => {
    const timer = window.setTimeout(load, 250)
    return () => window.clearTimeout(timer)
  }, [load])

  useEffect(() => {
    api.listOrganizers({ page_size: 100 }).then((r) => setOrganizers(r.items)).catch(() => undefined)
    api.listVenues({ page_size: 100 }).then((r) => setVenues(r.items)).catch(() => undefined)
  }, [])

  const pages = Math.max(1, Math.ceil(total / pageSize))

  const openCreate = () => {
    setForm({ ...emptyForm, event_date: new Date().toISOString().slice(0, 10) })
    setEditingId(null)
    setFormError(null)
    setModalOpen(true)
  }

  const openEdit = (event: EventItem) => {
    setForm({
      event_name: event.event_name,
      description: event.description ?? '',
      event_category: event.event_category,
      organizer_id: String(event.organizer_id),
      venue_id: String(event.venue_id),
      event_date: event.event_date,
      start_time: event.start_time?.slice(0, 5) ?? '10:00',
      end_time: event.end_time?.slice(0, 5) ?? '12:00',
      capacity: String(event.capacity),
      ticket_price: String(event.ticket_price),
      event_status: event.event_status,
    })
    setEditingId(event.event_id)
    setFormError(null)
    setModalOpen(true)
  }

  const save = async () => {
    setSaving(true)
    setFormError(null)
    try {
      const payload = {
        ...form,
        organizer_id: Number(form.organizer_id),
        venue_id: Number(form.venue_id),
        capacity: Number(form.capacity),
        ticket_price: Number(form.ticket_price),
      }
      if (editingId) {
        await api.updateEvent(editingId, payload)
        toast.push(`Event “${form.event_name}” was updated.`)
      } else {
        await api.createEvent(payload)
        toast.push(`Event “${form.event_name}” was created.`)
      }
      setModalOpen(false)
      load()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (event: EventItem) => {
    if (!window.confirm(`Delete “${event.event_name}”? This can not be undone.`)) return
    try {
      await api.deleteEvent(event.event_id)
      toast.push('Event deleted.')
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const columns: Column<EventItem>[] = (() => [
      {
        key: 'event_name',
        header: 'Event',
        render: (event) => (
          <div>
            <div className="cell-title">{event.event_name}</div>
            <div className="cell-sub">{event.event_category}</div>
          </div>
        ),
      },
      {
        key: 'event_date',
        header: 'Date & time',
        render: (event) => (
          <div className="nowrap">
            <div>{event.event_date}</div>
            <div className="cell-sub mono">
              {event.start_time?.slice(0, 5)} – {event.end_time?.slice(0, 5)}
            </div>
          </div>
        ),
      },
      {
        key: 'venue_name',
        header: 'Venue / organizer',
        render: (event) => (
          <div>
            <div>{event.venue_name}</div>
            <div className="cell-sub">{event.organizer_name}</div>
          </div>
        ),
      },
      {
        key: 'capacity',
        header: 'Capacity',
        align: 'right',
        render: (event) => (
          <div>
            <div className="strong">
              {event.registration_count}/{event.capacity}
            </div>
            <div className="progress" style={{ marginLeft: 'auto', marginTop: 4 }}>
              <div
                className={`progress__bar ${event.fill_rate_percent >= 100 ? 'progress__bar--danger' : event.fill_rate_percent >= 75 ? 'progress__bar--warning' : ''}`}
                style={{ width: `${Math.min(100, event.fill_rate_percent)}%` }}
              />
            </div>
          </div>
        ),
      },
      {
        key: 'ticket_price',
        header: 'Ticket',
        align: 'right',
        render: (event) => (
          <div>
            <div>{event.ticket_price > 0 ? money(event.ticket_price) : 'Free'}</div>
            <div className="cell-sub">{event.confirmed_count} confirmed</div>
          </div>
        ),
      },
      {
        key: 'event_status',
        header: 'Status',
        render: (event) => <StatusBadge value={event.event_status} />,
      },
      {
        key: 'actions',
        header: 'Actions',
        render: (event) => (
          <div className="btn-row">
            <button type="button" className="btn btn--ghost btn--sm" onClick={() => setDetail(event)}>
              View
            </button>
            <button type="button" className="btn btn--ghost btn--sm" onClick={() => openEdit(event)}>
              <IconEdit width={14} height={14} />
            </button>
            <button type="button" className="btn btn--danger btn--sm" onClick={() => remove(event)}>
              <IconTrash width={14} height={14} />
            </button>
          </div>
        ),
      },
    ])()

  return (
    <>
      <div className="card">
        <div className="card__header">
          <div>
            <h3>Event catalogue</h3>
            <p>{total} event(s) match the current filters</p>
          </div>
          <div className="btn-row">
            <button type="button" className="btn btn--ghost btn--sm" onClick={load}>
              <IconRefresh width={14} height={14} /> Refresh
            </button>
            <button type="button" className="btn btn--primary" onClick={openCreate}>
              <IconPlus width={15} height={15} /> Add event
            </button>
          </div>
        </div>

        <div className="card__body">
          <div className="filters">
            <div className="field field--grow">
              <label>Search</label>
              <input
                value={search}
                placeholder="Name, description or category"
                onChange={(event) => {
                  setSearch(event.target.value)
                  setPage(1)
                }}
              />
            </div>
            <SelectField
              label="Category"
              value={category}
              onChange={(value) => {
                setCategory(value)
                setPage(1)
              }}
              options={[{ value: '', label: 'All categories' }, ...CATEGORIES.map((item) => ({ value: item, label: item }))]}
            />
            <SelectField
              label="Status"
              value={status}
              onChange={(value) => {
                setStatus(value)
                setPage(1)
              }}
              options={[{ value: '', label: 'All statuses' }, ...STATUSES.map((item) => ({ value: item, label: item }))]}
            />
            <SelectField
              label="Organizer"
              value={organizerId}
              onChange={(value) => {
                setOrganizerId(value)
                setPage(1)
              }}
              options={[
                { value: '', label: 'All organizers' },
                ...organizers.map((item) => ({ value: String(item.organizer_id), label: item.organizer_name })),
              ]}
            />
            <SelectField
              label="Venue"
              value={venueId}
              onChange={(value) => {
                setVenueId(value)
                setPage(1)
              }}
              options={[
                { value: '', label: 'All venues' },
                ...venues.map((item) => ({ value: String(item.venue_id), label: item.venue_name })),
              ]}
            />
          </div>
        </div>

        {error ? (
          <div className="card__body">
            <div className="alert alert--error">{error}</div>
          </div>
        ) : null}

        <DataTable columns={columns} rows={events} rowKey={(event) => event.event_id} loading={loading} />

        <div className="pagination">
          <span>
            Page {page} of {pages} · {total} event(s)
          </span>
          <div className="pagination__buttons">
            <button type="button" className="btn btn--ghost btn--sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </button>
            <button
              type="button"
              className="btn btn--ghost btn--sm"
              disabled={page >= pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
            <select value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
              {[10, 20, 50].map((size) => (
                <option key={size} value={size}>
                  {size} / page
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <Modal
        open={modalOpen}
        title={editingId ? 'Edit event' : 'New event'}
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <button type="button" className="btn btn--ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn--primary" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : editingId ? 'Save changes' : 'Create event'}
            </button>
          </>
        }
      >
        {formError ? <div className="alert alert--error" style={{ marginBottom: 14 }}>{formError}</div> : null}
        <div className="form-grid">
          <InputField
            label="Event name"
            value={form.event_name}
            onChange={(value) => setForm({ ...form, event_name: value })}
            placeholder="e.g. Spring Product Launch"
            required
            full
          />
          <TextAreaField
            label="Description"
            value={form.description}
            onChange={(value) => setForm({ ...form, description: value })}
          />
          <SelectField
            label="Category"
            value={form.event_category}
            onChange={(value) => setForm({ ...form, event_category: value })}
            options={CATEGORIES.map((item) => ({ value: item, label: item }))}
          />
          <SelectField
            label="Organizer"
            value={form.organizer_id}
            onChange={(value) => setForm({ ...form, organizer_id: value })}
            options={[
              { value: '', label: 'Select an organizer' },
              ...organizers.map((item) => ({ value: String(item.organizer_id), label: `${item.organizer_name} · ${item.organization_name ?? ''}` })),
            ]}
          />
          <SelectField
            label="Venue"
            value={form.venue_id}
            onChange={(value) => setForm({ ...form, venue_id: value })}
            options={[
              { value: '', label: 'Select a venue' },
              ...venues.map((item) => ({
                value: String(item.venue_id),
                label: `${item.venue_name} (${item.capacity} seats)`,
              })),
            ]}
          />
          <InputField
            label="Date"
            type="date"
            value={form.event_date}
            onChange={(value) => setForm({ ...form, event_date: value })}
            required
          />
          <InputField
            label="Start time"
            type="time"
            value={form.start_time}
            onChange={(value) => setForm({ ...form, start_time: value })}
            required
          />
          <InputField
            label="End time"
            type="time"
            value={form.end_time}
            onChange={(value) => setForm({ ...form, end_time: value })}
            required
          />
          <InputField
            label="Capacity"
            type="number"
            min={1}
            value={form.capacity}
            onChange={(value) => setForm({ ...form, capacity: value })}
            required
          />
          <InputField
            label="Ticket price (₹)"
            type="number"
            min={0}
            step="0.01"
            value={form.ticket_price}
            onChange={(value) => setForm({ ...form, ticket_price: value })}
          />
          <SelectField
            label="Status"
            value={form.event_status}
            onChange={(value) => setForm({ ...form, event_status: value })}
            options={STATUSES.map((item) => ({ value: item, label: item }))}
          />
        </div>
        <div className="alert alert--info" style={{ marginTop: 16 }}>
          The backend rejects an event whose capacity is larger than the venue capacity and also rejects
          overlapping bookings for the same venue and time slot.
        </div>
      </Modal>

      <Modal
        open={detail !== null}
        title={detail?.event_name ?? ''}
        onClose={() => setDetail(null)}
        footer={
          <button type="button" className="btn btn--ghost" onClick={() => setDetail(null)}>
            Close
          </button>
        }
      >
        {detail ? (
          <div className="stack">
            <div className="row row--between">
              <StatusBadge value={detail.event_status} />
              <span className="badge badge--accent">{detail.event_category}</span>
            </div>
            <p className="muted" style={{ margin: 0 }}>
              {detail.description}
            </p>
            <dl className="detail-list">
              <dt>Date</dt>
              <dd>{detail.event_date}</dd>
              <dt>Time</dt>
              <dd className="mono">
                {detail.start_time?.slice(0, 5)} – {detail.end_time?.slice(0, 5)}
              </dd>
              <dt>Venue</dt>
              <dd>
                {detail.venue_name} · {detail.venue_location}
              </dd>
              <dt>Organizer</dt>
              <dd>
                {detail.organizer_name} · {detail.organization_name}
              </dd>
              <dt>Capacity</dt>
              <dd>
                {detail.registration_count} registered of {detail.capacity} ({detail.fill_rate_percent}%)
              </dd>
              <dt>Confirmed</dt>
              <dd>{detail.confirmed_count}</dd>
              <dt>Present</dt>
              <dd>{detail.present_count}</dd>
              <dt>Seats available</dt>
              <dd>{detail.seats_available}</dd>
              <dt>Ticket price</dt>
              <dd>{detail.ticket_price > 0 ? money(detail.ticket_price) : 'Free event'}</dd>
            </dl>
          </div>
        ) : null}
      </Modal>
    </>
  )
}
