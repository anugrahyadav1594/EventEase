/**
 * Thin wrapper around the EventEase REST API.
 *
 * The base URL is empty by default so that the Vite dev server proxy
 * (`/api` -> FastAPI) is used.  A completely deployed frontend can set
 * `VITE_API_BASE_URL=https://api.example.com/api`.
 */
import type {
  Attendee,
  Dashboard,
  EventItem,
  Health,
  LabExperimentResult,
  LabExperimentSummary,
  Organizer,
  Paginated,
  Payment,
  Registration,
  ReportResult,
  Venue,
} from '../types'

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type Query = Record<string, string | number | boolean | undefined | null>

function buildUrl(path: string, query?: Query): string {
  const url = `${API_BASE}${path}`
  if (!query) return url
  const params = new URLSearchParams()
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  })
  const search = params.toString()
  return search ? `${url}?${search}` : url
}

async function request<T>(path: string, options: RequestInit = {}, query?: Query): Promise<T> {
  const response = await fetch(buildUrl(path, query), {
    headers: options.body ? { 'Content-Type': 'application/json' } : undefined,
    ...options,
  })

  if (!response.ok) {
    let detail = `The request failed (HTTP ${response.status}).`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') {
        detail = body.detail
      } else if (Array.isArray(body?.detail)) {
        detail = body.detail.map((item: any) => item?.msg ?? JSON.stringify(item)).join(' · ')
      }
    } catch {
      /* the response body was not JSON */
    }
    throw new ApiError(detail, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

const json = (payload: unknown): RequestInit => ({
  method: 'POST',
  body: JSON.stringify(payload),
})

const put = (payload: unknown): RequestInit => ({
  method: 'PUT',
  body: JSON.stringify(payload),
})

const patch = (payload: unknown): RequestInit => ({
  method: 'PATCH',
  body: JSON.stringify(payload),
})

export const api = {
  health: () => request<Health>('/health'),
  dashboard: () => request<Dashboard>('/dashboard'),

  // ------------------------------------------------------------ organizers
  listOrganizers: (query?: Query) => request<Paginated<Organizer>>('/organizers', {}, query),
  createOrganizer: (payload: unknown) => request<Organizer>('/organizers', json(payload)),
  updateOrganizer: (id: number, payload: unknown) => request<Organizer>(`/organizers/${id}`, put(payload)),
  deleteOrganizer: (id: number) => request<{ message: string }>(`/organizers/${id}`, { method: 'DELETE' }),

  // ---------------------------------------------------------------- venues
  listVenues: (query?: Query) => request<Paginated<Venue>>('/venues', {}, query),
  getVenueEvents: (id: number) => request<Record<string, any>[]>(`/venues/${id}/events`),
  createVenue: (payload: unknown) => request<Venue>('/venues', json(payload)),
  updateVenue: (id: number, payload: unknown) => request<Venue>(`/venues/${id}`, put(payload)),
  deleteVenue: (id: number) => request<{ message: string }>(`/venues/${id}`, { method: 'DELETE' }),

  // ---------------------------------------------------------------- events
  listEvents: (query?: Query) => request<Paginated<EventItem>>('/events', {}, query),
  getEvent: (id: number) => request<EventItem>(`/events/${id}`),
  createEvent: (payload: unknown) => request<EventItem>('/events', json(payload)),
  updateEvent: (id: number, payload: unknown) => request<EventItem>(`/events/${id}`, put(payload)),
  deleteEvent: (id: number) => request<{ message: string }>(`/events/${id}`, { method: 'DELETE' }),

  // ------------------------------------------------------------- attendees
  listAttendees: (query?: Query) => request<Paginated<Attendee>>('/attendees', {}, query),
  getAttendee: (id: number) => request<Attendee>(`/attendees/${id}`),
  getAttendeeRegistrations: (id: number) => request<Record<string, any>[]>(`/attendees/${id}/registrations`),
  createAttendee: (payload: unknown) => request<Attendee>('/attendees', json(payload)),
  updateAttendee: (id: number, payload: unknown) => request<Attendee>(`/attendees/${id}`, put(payload)),
  deleteAttendee: (id: number) => request<{ message: string }>(`/attendees/${id}`, { method: 'DELETE' }),

  // --------------------------------------------------------- registrations
  listRegistrations: (query?: Query) =>
    request<{ items: Registration[]; total: number }>('/registrations', {}, query),
  createRegistration: (payload: unknown) => request<Registration>('/registrations', json(payload)),
  updateRegistrationStatus: (id: number, status: string) =>
    request<Registration>(`/registrations/${id}/status`, patch({ registration_status: status })),
  updateAttendance: (id: number, status: string) =>
    request<Registration>(`/registrations/${id}/attendance`, patch({ attendance_status: status })),

  // -------------------------------------------------------------- payments
  listPayments: (query?: Query) =>
    request<{ items: Payment[]; total: number; summary: Record<string, number> }>('/payments', {}, query),
  createPayment: (payload: unknown) => request<Payment>('/payments', json(payload)),
  updatePaymentStatus: (id: number, status: string) =>
    request<Payment>(`/payments/${id}/status`, patch({ payment_status: status })),

  // --------------------------------------------------------------- reports
  listReports: () =>
    request<
      { key: string; title: string; concept: string; description: string; endpoint: string }[]
    >('/reports'),
  getReport: (key: string, query?: Query) => request<ReportResult>(`/reports/${key}`, {}, query),

  // --------------------------------------------------------------- sql lab
  listExperiments: () => request<LabExperimentSummary[]>('/sql-lab/experiments'),
  runExperiment: (key: string, params: Record<string, number> = {}) =>
    request<LabExperimentResult>(`/sql-lab/experiments/${key}/run`, json(params)),
}

export default api
