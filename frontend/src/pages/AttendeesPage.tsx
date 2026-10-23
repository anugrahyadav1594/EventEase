/** Attendee management with the registration history of every participant. */
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import type { Attendee } from '../types'
import DataTable from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { InputField } from '../components/Form'
import Modal from '../components/Modal'
import StatusBadge from '../components/StatusBadge'
import { useToast } from '../components/Toast'
import { IconEdit, IconPlus, IconTrash } from '../components/Icons'

const money = (value: number) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`

const emptyForm = {
  full_name: '',
  email: '',
  phone: '',
  organization: '',
}

export default function AttendeesPage() {
  const toast = useToast()
  const [attendees, setAttendees] = useState<Attendee[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({ ...emptyForm })
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [history, setHistory] = useState<{ attendee: Attendee; rows: Record<string, any>[] } | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.listAttendees({ search: search || undefined, page_size: 100 })
      setAttendees(response.items)
      setTotal(response.total)
    } catch (err: any) {
      toast.push(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [search, toast])

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

  const openEdit = (attendee: Attendee) => {
    setForm({
      full_name: attendee.full_name,
      email: attendee.email,
      phone: attendee.phone ?? '',
      organization: attendee.organization ?? '',
    })
    setEditingId(attendee.attendee_id)
    setFormError(null)
    setModalOpen(true)
  }

  const save = async () => {
    setSaving(true)
    setFormError(null)
    try {
      if (editingId) {
        await api.updateAttendee(editingId, form)
        toast.push('Attendee updated.')
      } else {
        await api.createAttendee(form)
        toast.push('Attendee created.')
      }
      setModalOpen(false)
      load()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (attendee: Attendee) => {
    if (!window.confirm(`Delete “${attendee.full_name}”?`)) return
    try {
      await api.deleteAttendee(attendee.attendee_id)
      toast.push('Attendee deleted.')
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const openHistory = async (attendee: Attendee) => {
    try {
      const rows = await api.getAttendeeRegistrations(attendee.attendee_id)
      setHistory({ attendee, rows })
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const columns: Column<Attendee>[] = [
    {
      key: 'full_name',
      header: 'Attendee',
      render: (attendee) => (
        <div>
          <div className="cell-title">{attendee.full_name}</div>
          <div className="cell-sub">{attendee.email}</div>
        </div>
      ),
    },
    {
      key: 'organization',
      header: 'Organisation',
      render: (attendee) => attendee.organization ?? '—',
    },
    {
      key: 'phone',
      header: 'Phone',
      render: (attendee) => attendee.phone ?? '—',
    },
    {
      key: 'total_registrations',
      header: 'Registrations',
      align: 'right',
      render: (attendee) => attendee.total_registrations,
    },
    {
      key: 'events_attended',
      header: 'Attended',
      align: 'right',
      render: (attendee) => attendee.events_attended,
    },
    {
      key: 'total_paid',
      header: 'Paid',
      align: 'right',
      render: (attendee) => money(attendee.total_paid),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (attendee) => (
        <div className="btn-row">
          <button type="button" className="btn btn--ghost btn--sm" onClick={() => openHistory(attendee)}>
            History
          </button>
          <button type="button" className="btn btn--ghost btn--sm" onClick={() => openEdit(attendee)}>
            <IconEdit width={14} height={14} />
          </button>
          <button type="button" className="btn btn--danger btn--sm" onClick={() => remove(attendee)}>
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
            <h3>Attendees</h3>
            <p>{total} attendee(s) · e-mail addresses are unique</p>
          </div>
          <button type="button" className="btn btn--primary" onClick={openCreate}>
            <IconPlus width={15} height={15} /> Add attendee
          </button>
        </div>

        <div className="card__body">
          <div className="filters">
            <div className="field field--grow">
              <label>Search</label>
              <input
                value={search}
                placeholder="Name, e-mail or organisation"
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
          </div>
        </div>

        <DataTable columns={columns} rows={attendees} rowKey={(attendee) => attendee.attendee_id} loading={loading} />
      </div>

      <Modal
        open={modalOpen}
        title={editingId ? 'Edit attendee' : 'New attendee'}
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <button type="button" className="btn btn--ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn--primary" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Save attendee'}
            </button>
          </>
        }
      >
        {formError ? <div className="alert alert--error" style={{ marginBottom: 14 }}>{formError}</div> : null}
        <div className="form-grid">
          <InputField
            label="Full name"
            value={form.full_name}
            onChange={(value) => setForm({ ...form, full_name: value })}
            required
          />
          <InputField
            label="E-mail"
            type="email"
            value={form.email}
            onChange={(value) => setForm({ ...form, email: value })}
            required
          />
          <InputField
            label="Phone"
            value={form.phone}
            onChange={(value) => setForm({ ...form, phone: value })}
          />
          <InputField
            label="Organisation"
            value={form.organization}
            onChange={(value) => setForm({ ...form, organization: value })}
          />
        </div>
      </Modal>

      <Modal
        open={history !== null}
        title={history ? `Registration history · ${history.attendee.full_name}` : ''}
        onClose={() => setHistory(null)}
        footer={
          <button type="button" className="btn btn--ghost" onClick={() => setHistory(null)}>
            Close
          </button>
        }
      >
        {history ? (
          <div className="stack">
            <dl className="detail-list">
              <dt>E-mail</dt>
              <dd>{history.attendee.email}</dd>
              <dt>Registrations</dt>
              <dd>{history.attendee.total_registrations}</dd>
              <dt>Events attended</dt>
              <dd>{history.attendee.events_attended}</dd>
              <dt>Total paid</dt>
              <dd>{money(history.attendee.total_paid)}</dd>
            </dl>
            <div className="table-wrap">
              <table className="data">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th>Registered on</th>
                    <th>Status</th>
                    <th>Attendance</th>
                    <th className="num">Ticket</th>
                  </tr>
                </thead>
                <tbody>
                  {history.rows.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="muted">
                        This attendee has not registered for any event yet.
                      </td>
                    </tr>
                  ) : (
                    history.rows.map((row: any) => (
                      <tr key={row.registration_id}>
                        <td>Event #{row.event_id}</td>
                        <td className="nowrap">{row.registration_date?.slice(0, 10)}</td>
                        <td>
                          <StatusBadge value={row.registration_status} />
                        </td>
                        <td>
                          <StatusBadge value={row.attendance_status} />
                        </td>
                        <td className="num">{money(row.ticket_price)}</td>
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
