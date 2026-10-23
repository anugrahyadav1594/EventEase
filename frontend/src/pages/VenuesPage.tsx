/** Venue management including the scheduled events of every venue. */
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import type { Venue } from '../types'
import DataTable from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { InputField, SelectField } from '../components/Form'
import Modal from '../components/Modal'
import StatusBadge from '../components/StatusBadge'
import { useToast } from '../components/Toast'
import { IconEdit, IconPlus, IconTrash } from '../components/Icons'

const AVAILABILITY = ['Available', 'Unavailable', 'Maintenance']

const emptyForm = {
  venue_name: '',
  location: '',
  capacity: '100',
  venue_type: '',
  availability_status: 'Available',
}

export default function VenuesPage() {
  const toast = useToast()
  const [venues, setVenues] = useState<Venue[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [availability, setAvailability] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({ ...emptyForm })
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [detail, setDetail] = useState<{ venue: Venue; events: Record<string, any>[] } | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.listVenues({
        search: search || undefined,
        availability_status: availability || undefined,
        page_size: 100,
      })
      setVenues(response.items)
      setTotal(response.total)
    } catch (err: any) {
      toast.push(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [search, availability, toast])

  useEffect(() => {
    const timer = window.setTimeout(load, 250)
    return () => window.clearTimeout(timer)
  }, [load])

  const openCreate = () => {
    setForm({ ...emptyForm })
    setEditingId(null)
    setFormError(null)
    setModalOpen(true)
  }

  const openEdit = (venue: Venue) => {
    setForm({
      venue_name: venue.venue_name,
      location: venue.location,
      capacity: String(venue.capacity),
      venue_type: venue.venue_type ?? '',
      availability_status: venue.availability_status,
    })
    setEditingId(venue.venue_id)
    setFormError(null)
    setModalOpen(true)
  }

  const save = async () => {
    setSaving(true)
    setFormError(null)
    try {
      const payload = { ...form, capacity: Number(form.capacity) }
      if (editingId) {
        await api.updateVenue(editingId, payload)
        toast.push('Venue updated.')
      } else {
        await api.createVenue(payload)
        toast.push('Venue created.')
      }
      setModalOpen(false)
      load()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (venue: Venue) => {
    if (!window.confirm(`Delete “${venue.venue_name}”?`)) return
    try {
      await api.deleteVenue(venue.venue_id)
      toast.push('Venue deleted.')
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const openDetail = async (venue: Venue) => {
    try {
      const events = await api.getVenueEvents(venue.venue_id)
      setDetail({ venue, events })
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const columns: Column<Venue>[] = [
    {
      key: 'venue_name',
      header: 'Venue',
      render: (venue) => (
        <div>
          <div className="cell-title">{venue.venue_name}</div>
          <div className="cell-sub">{venue.location}</div>
        </div>
      ),
    },
    {
      key: 'venue_type',
      header: 'Type',
      render: (venue) => venue.venue_type ?? '—',
    },
    {
      key: 'capacity',
      header: 'Capacity',
      align: 'right',
      render: (venue) => venue.capacity,
    },
    {
      key: 'events_hosted',
      header: 'Events',
      align: 'right',
      render: (venue) => venue.events_hosted,
    },
    {
      key: 'utilization_percent',
      header: 'Utilisation',
      align: 'right',
      render: (venue) => (
        <div>
          <div className="strong">{venue.utilization_percent}%</div>
          <div className="progress" style={{ marginLeft: 'auto', marginTop: 4 }}>
            <div
              className={`progress__bar ${venue.utilization_percent >= 80 ? 'progress__bar--warning' : ''}`}
              style={{ width: `${Math.min(100, venue.utilization_percent)}%` }}
            />
          </div>
        </div>
      ),
    },
    {
      key: 'availability_status',
      header: 'Availability',
      render: (venue) => <StatusBadge value={venue.availability_status} />,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (venue) => (
        <div className="btn-row">
          <button type="button" className="btn btn--ghost btn--sm" onClick={() => openDetail(venue)}>
            Schedule
          </button>
          <button type="button" className="btn btn--ghost btn--sm" onClick={() => openEdit(venue)}>
            <IconEdit width={14} height={14} />
          </button>
          <button type="button" className="btn btn--danger btn--sm" onClick={() => remove(venue)}>
            <IconTrash width={14} height={14} />
          </button>
        </div>
      ),
    },
  ]

  return (
    <>
      <div className="card">
        <div className="card__header">
          <div>
            <h3>Venues</h3>
            <p>{total} venue(s) · capacity and double booking rules are enforced by the backend</p>
          </div>
          <button type="button" className="btn btn--primary" onClick={openCreate}>
            <IconPlus width={15} height={15} /> Add venue
          </button>
        </div>

        <div className="card__body">
          <div className="filters">
            <div className="field field--grow">
              <label>Search</label>
              <input
                value={search}
                placeholder="Venue name or location"
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
            <SelectField
              label="Availability"
              value={availability}
              onChange={setAvailability}
              options={[
                { value: '', label: 'All venues' },
                ...AVAILABILITY.map((item) => ({ value: item, label: item })),
              ]}
            />
          </div>
        </div>

        <DataTable columns={columns} rows={venues} rowKey={(venue) => venue.venue_id} loading={loading} />
      </div>

      <Modal
        open={modalOpen}
        title={editingId ? 'Edit venue' : 'New venue'}
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <button type="button" className="btn btn--ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn--primary" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Save venue'}
            </button>
          </>
        }
      >
        {formError ? <div className="alert alert--error" style={{ marginBottom: 14 }}>{formError}</div> : null}
        <div className="form-grid">
          <InputField
            label="Venue name"
            value={form.venue_name}
            onChange={(value) => setForm({ ...form, venue_name: value })}
            required
          />
          <InputField
            label="Location"
            value={form.location}
            onChange={(value) => setForm({ ...form, location: value })}
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
            label="Venue type"
            value={form.venue_type}
            onChange={(value) => setForm({ ...form, venue_type: value })}
            placeholder="Auditorium, Lab, Stadium…"
          />
          <SelectField
            label="Availability"
            value={form.availability_status}
            onChange={(value) => setForm({ ...form, availability_status: value })}
            options={AVAILABILITY.map((item) => ({ value: item, label: item }))}
            full
          />
        </div>
      </Modal>

      <Modal
        open={detail !== null}
        title={detail ? `Schedule · ${detail.venue.venue_name}` : ''}
        onClose={() => setDetail(null)}
        size="md"
        footer={
          <button type="button" className="btn btn--ghost" onClick={() => setDetail(null)}>
            Close
          </button>
        }
      >
        {detail ? (
          <div className="stack">
            <dl className="detail-list">
              <dt>Location</dt>
              <dd>{detail.venue.location}</dd>
              <dt>Capacity</dt>
              <dd>{detail.venue.capacity} seats</dd>
              <dt>Availability</dt>
              <dd>
                <StatusBadge value={detail.venue.availability_status} />
              </dd>
              <dt>Registrations</dt>
              <dd>{detail.venue.total_registrations}</dd>
            </dl>
            <div className="table-wrap">
              <table className="data">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th className="num">Registrations</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.events.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="muted">
                        No event is scheduled in this venue yet.
                      </td>
                    </tr>
                  ) : (
                    detail.events.map((event: any) => (
                      <tr key={event.event_id}>
                        <td>{event.event_name}</td>
                        <td className="nowrap">{event.event_date}</td>
                        <td className="nowrap mono">
                          {event.start_time?.slice(0, 5)} – {event.end_time?.slice(0, 5)}
                        </td>
                        <td className="num">{event.registration_count}</td>
                        <td>
                          <StatusBadge value={event.event_status} />
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </Modal>
    </>
  )
}
