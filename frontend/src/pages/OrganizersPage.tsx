/** Organizer management. */
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import type { Organizer } from '../types'
import DataTable from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { InputField } from '../components/Form'
import Modal from '../components/Modal'
import { useToast } from '../components/Toast'
import { IconEdit, IconPlus, IconTrash } from '../components/Icons'

const emptyForm = {
  organizer_name: '',
  email: '',
  phone: '',
  organization_name: '',
}

export default function OrganizersPage() {
  const toast = useToast()
  const [organizers, setOrganizers] = useState<Organizer[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({ ...emptyForm })
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.listOrganizers({ search: search || undefined, page_size: 100 })
      setOrganizers(response.items)
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

  const openEdit = (organizer: Organizer) => {
    setForm({
      organizer_name: organizer.organizer_name,
      email: organizer.email,
      phone: organizer.phone ?? '',
      organization_name: organizer.organization_name ?? '',
    })
    setEditingId(organizer.organizer_id)
    setFormError(null)
    setModalOpen(true)
  }

  const save = async () => {
    setSaving(true)
    setFormError(null)
    try {
      if (editingId) {
        await api.updateOrganizer(editingId, form)
        toast.push('Organizer updated.')
      } else {
        await api.createOrganizer(form)
        toast.push('Organizer created.')
      }
      setModalOpen(false)
      load()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (organizer: Organizer) => {
    if (!window.confirm(`Delete “${organizer.organizer_name}”?`)) return
    try {
      await api.deleteOrganizer(organizer.organizer_id)
      toast.push('Organizer deleted.')
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const columns: Column<Organizer>[] = [
    {
      key: 'organizer_name',
      header: 'Organizer',
      render: (organizer) => (
        <div>
          <div className="cell-title">{organizer.organizer_name}</div>
          <div className="cell-sub">{organizer.organization_name ?? 'Independent'}</div>
        </div>
      ),
    },
    {
      key: 'email',
      header: 'E-mail',
      render: (organizer) => organizer.email,
    },
    {
      key: 'phone',
      header: 'Phone',
      render: (organizer) => organizer.phone ?? '—',
    },
    {
      key: 'events_managed',
      header: 'Events managed',
      align: 'right',
      render: (organizer) => organizer.events_managed,
    },
    {
      key: 'total_registrations',
      header: 'Registrations',
      align: 'right',
      render: (organizer) => organizer.total_registrations,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (organizer) => (
        <div className="btn-row">
          <button type="button" className="btn btn--ghost btn--sm" onClick={() => openEdit(organizer)}>
            <IconEdit width={14} height={14} />
          </button>
          <button type="button" className="btn btn--danger btn--sm" onClick={() => remove(organizer)}>
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
            <h3>Organizers</h3>
            <p>{total} organizer(s) · search by name or organisation</p>
          </div>
          <button type="button" className="btn btn--primary" onClick={openCreate}>
            <IconPlus width={15} height={15} /> Add organizer
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

        <DataTable columns={columns} rows={organizers} rowKey={(organizer) => organizer.organizer_id} loading={loading} />
      </div>

      <Modal
        open={modalOpen}
        title={editingId ? 'Edit organizer' : 'New organizer'}
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <button type="button" className="btn btn--ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn--primary" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Save organizer'}
            </button>
          </>
        }
      >
        {formError ? <div className="alert alert--error" style={{ marginBottom: 14 }}>{formError}</div> : null}
        <div className="form-grid">
          <InputField
            label="Name"
            value={form.organizer_name}
            onChange={(value) => setForm({ ...form, organizer_name: value })}
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
            value={form.organization_name}
            onChange={(value) => setForm({ ...form, organization_name: value })}
            full
          />
        </div>
      </Modal>
    </>
  )
}
