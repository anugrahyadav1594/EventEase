/** Payment management: record payments, track refunds and revenue. */
import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import type { Payment, Registration } from '../types'
import DataTable from '../components/DataTable'
import type { Column } from '../components/DataTable'
import { InputField, SelectField } from '../components/Form'
import Modal from '../components/Modal'
import StatusBadge from '../components/StatusBadge'
import { useToast } from '../components/Toast'
import KpiCard from '../components/KpiCard'
import { IconCard, IconCheck, IconMoney, IconRefresh } from '../components/Icons'

const METHODS = ['Cash', 'UPI', 'Card', 'Bank Transfer']
const STATUSES = ['Pending', 'Completed', 'Refunded']

const money = (value: number) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`

export default function PaymentsPage() {
  const toast = useToast()
  const [payments, setPayments] = useState<Payment[]>([])
  const [summary, setSummary] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState('')
  const [method, setMethod] = useState('')
  const [registrations, setRegistrations] = useState<Registration[]>([])

  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({
    registration_id: '',
    amount: '',
    payment_method: 'UPI',
    payment_status: 'Pending',
    transaction_reference: '',
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.listPayments({
        status: status || undefined,
        method: method || undefined,
      })
      setPayments(response.items)
      setSummary(response.summary)
    } catch (err: any) {
      toast.push(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [status, method, toast])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    api.listRegistrations({}).then((response) => setRegistrations(response.items)).catch(() => undefined)
  }, [])

  const openCreate = () => {
    setForm({
      registration_id: '',
      amount: '',
      payment_method: 'UPI',
      payment_status: 'Pending',
      transaction_reference: '',
    })
    setFormError(null)
    setModalOpen(true)
  }

  const save = async () => {
    setSaving(true)
    setFormError(null)
    try {
      const payload: Record<string, unknown> = {
        registration_id: Number(form.registration_id),
        amount: Number(form.amount),
        payment_method: form.payment_method,
        payment_status: form.payment_status,
      }
      if (form.transaction_reference) {
        payload.transaction_reference = form.transaction_reference
      }
      await api.createPayment(payload)
      toast.push('Payment recorded.')
      setModalOpen(false)
      load()
    } catch (err: any) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const changeStatus = async (payment: Payment, next: string) => {
    try {
      await api.updatePaymentStatus(payment.payment_id, next)
      toast.push(`Payment ${payment.payment_id} → ${next}.`)
      load()
    } catch (err: any) {
      toast.push(err.message, 'error')
    }
  }

  const columns: Column<Payment>[] = [
    {
      key: 'payment_id',
      header: 'Payment',
      render: (payment) => (
        <div>
          <div className="cell-title">#{payment.payment_id}</div>
          <div className="cell-sub mono">{payment.transaction_reference ?? 'no reference'}</div>
        </div>
      ),
    },
    {
      key: 'attendee_name',
      header: 'Attendee / event',
      render: (payment) => (
        <div>
          <div>{payment.attendee_name}</div>
          <div className="cell-sub">{payment.event_name}</div>
        </div>
      ),
    },
    {
      key: 'amount',
      header: 'Amount',
      align: 'right',
      render: (payment) => <span className="strong">{money(payment.amount)}</span>,
    },
    {
      key: 'payment_method',
      header: 'Method',
      render: (payment) => <span className="badge badge--accent">{payment.payment_method}</span>,
    },
    {
      key: 'payment_status',
      header: 'Status',
      render: (payment) => <StatusBadge value={payment.payment_status} />,
    },
    {
      key: 'payment_date',
      header: 'Date',
      render: (payment) => payment.payment_date?.slice(0, 10) ?? '—',
    },
    {
      key: 'actions',
      header: 'Update',
      render: (payment) => (
        <select
          value={payment.payment_status}
          onChange={(event) => changeStatus(payment, event.target.value)}
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
      <section className="kpi-grid">
        <KpiCard
          label="Collected revenue"
          value={money(summary.collected ?? 0)}
          hint="completed payments only"
          tone="success"
          icon={<IconMoney />}
        />
        <KpiCard
          label="Pending amount"
          value={money(summary.outstanding ?? 0)}
          hint="not yet collected"
          tone="warning"
          icon={<IconCard />}
        />
        <KpiCard
          label="Refunded amount"
          value={money(summary.refunded ?? 0)}
          hint="never counted as revenue"
          tone="purple"
          icon={<IconRefresh />}
        />
        <KpiCard
          label="Payment records"
          value={payments.length}
          hint="shown by the current filter"
          icon={<IconCheck />}
        />
      </section>

      <div className="card">
        <div className="card__header">
          <div>
            <h3>Payments</h3>
            <p>Database backed payment records - no real payment gateway is involved</p>
          </div>
          <button type="button" className="btn btn--primary" onClick={openCreate}>
            <IconCard width={15} height={15} /> Record payment
          </button>
        </div>

        <div className="card__body">
          <div className="filters">
            <SelectField
              label="Status"
              value={status}
              onChange={setStatus}
              options={[{ value: '', label: 'All statuses' }, ...STATUSES.map((item) => ({ value: item, label: item }))]}
            />
            <SelectField
              label="Method"
              value={method}
              onChange={setMethod}
              options={[{ value: '', label: 'All methods' }, ...METHODS.map((item) => ({ value: item, label: item }))]}
            />
          </div>
        </div>

        <DataTable columns={columns} rows={payments} rowKey={(payment) => payment.payment_id} loading={loading} />
      </div>

      <Modal
        open={modalOpen}
        title="Record a payment"
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <button type="button" className="btn btn--ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn--primary" onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Save payment'}
            </button>
          </>
        }
      >
        {formError ? <div className="alert alert--error" style={{ marginBottom: 14 }}>{formError}</div> : null}
        <div className="form-grid">
          <SelectField
            label="Registration"
            value={form.registration_id}
            onChange={(value) => {
              const registration = registrations.find((item) => item.registration_id === Number(value))
              setForm({
                ...form,
                registration_id: value,
                amount: registration ? String(registration.ticket_price ?? '') : form.amount,
              })
            }}
            options={[
              { value: '', label: 'Select a registration' },
              ...registrations.map((registration) => ({
                value: String(registration.registration_id),
                label: `#${registration.registration_id} · ${registration.attendee_name} · ${registration.event_name}`,
              })),
            ]}
            full
          />
          <InputField
            label="Amount (₹)"
            type="number"
            min={0}
            step="0.01"
            value={form.amount}
            onChange={(value) => setForm({ ...form, amount: value })}
            required
          />
          <SelectField
            label="Method"
            value={form.payment_method}
            onChange={(value) => setForm({ ...form, payment_method: value })}
            options={METHODS.map((item) => ({ value: item, label: item }))}
          />
          <SelectField
            label="Status"
            value={form.payment_status}
            onChange={(value) => setForm({ ...form, payment_status: value })}
            options={STATUSES.map((item) => ({ value: item, label: item }))}
          />
          <InputField
            label="Transaction reference"
            value={form.transaction_reference}
            onChange={(value) => setForm({ ...form, transaction_reference: value })}
            placeholder="UPI / card reference (unique)"
            full
          />
        </div>
      </Modal>
    </>
  )
}
