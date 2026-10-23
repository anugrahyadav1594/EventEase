/** Shared types of the EventEase API. */

export type EventStatus = 'Upcoming' | 'Ongoing' | 'Completed' | 'Cancelled'
export type VenueAvailability = 'Available' | 'Unavailable' | 'Maintenance'
export type RegistrationStatus = 'Registered' | 'Confirmed' | 'Cancelled' | 'Waitlisted'
export type AttendanceStatus = 'Not Marked' | 'Present' | 'Absent'
export type PaymentMethod = 'Cash' | 'UPI' | 'Card' | 'Bank Transfer'
export type PaymentStatus = 'Pending' | 'Completed' | 'Refunded'

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface Health {
  status: string
  service: string
  database_connected: boolean
  dialect: string | null
  server_version: string | null
  row_counts: Record<string, number>
}

export interface DashboardMetrics {
  total_organizers: number
  total_venues: number
  total_events: number
  upcoming_events: number
  ongoing_events: number
  completed_events: number
  cancelled_events: number
  total_attendees: number
  total_registrations: number
  registered_registrations: number
  confirmed_registrations: number
  cancelled_registrations: number
  waitlisted_registrations: number
  present_count: number
  absent_count: number
  not_marked_count: number
  average_attendance_rate: number
  total_revenue: number
  pending_amount: number
  refunded_amount: number
  payment_records: number
}

export interface Dashboard {
  metrics: DashboardMetrics
  charts: {
    registrations_by_event: Record<string, any>[]
    revenue_by_category: Record<string, any>[]
    attendance_by_event: Record<string, any>[]
    venue_utilization: Record<string, any>[]
    events_by_category: Record<string, any>[]
  }
  popular_events: Record<string, any>[]
  upcoming_schedule: Record<string, any>[]
}

export interface Organizer {
  organizer_id: number
  organizer_name: string
  email: string
  phone: string | null
  organization_name: string | null
  created_at?: string | null
  events_managed: number
  total_registrations: number
}

export interface Venue {
  venue_id: number
  venue_name: string
  location: string
  capacity: number
  venue_type: string | null
  availability_status: VenueAvailability
  events_hosted: number
  total_registrations: number
  utilization_percent: number
}

export interface EventItem {
  event_id: number
  event_name: string
  description: string | null
  event_category: string
  organizer_id: number
  organizer_name: string | null
  organization_name: string | null
  venue_id: number
  venue_name: string | null
  venue_location: string | null
  event_date: string
  start_time: string
  end_time: string
  capacity: number
  ticket_price: number
  event_status: EventStatus
  created_at?: string | null
  registration_count: number
  confirmed_count: number
  present_count: number
  seats_available: number
  fill_rate_percent: number
  revenue: number
}

export interface Attendee {
  attendee_id: number
  full_name: string
  email: string
  phone: string | null
  organization: string | null
  registration_date?: string | null
  total_registrations: number
  events_attended: number
  total_paid: number
}

export interface Registration {
  registration_id: number
  attendee_id: number
  attendee_name: string | null
  attendee_email: string | null
  event_id: number
  event_name: string | null
  event_category: string | null
  event_date: string | null
  venue_name: string | null
  registration_date: string | null
  registration_status: RegistrationStatus
  attendance_status: AttendanceStatus
  ticket_type: string | null
  ticket_price: number
  payment_status: string | null
  amount_paid: number
}

export interface Payment {
  payment_id: number
  registration_id: number
  attendee_id: number | null
  attendee_name: string | null
  event_id: number | null
  event_name: string | null
  amount: number
  payment_method: PaymentMethod
  payment_status: PaymentStatus
  transaction_reference: string | null
  payment_date: string | null
}

export interface ReportResult {
  key: string
  title: string
  concept: string
  description: string
  explanation: string
  sql: string
  params: Record<string, any>
  columns: string[]
  rows: Record<string, any>[]
  row_count: number
}

export interface LabStep {
  label: string
  sql: string
  status: 'ok' | 'error'
  message: string | null
  row_count: number
  columns: string[]
  rows: Record<string, any>[]
  note?: string
}

export interface LabExperimentSummary {
  key: string
  number: number
  title: string
  concept: string
  description: string
  statement_count: number
  notes: string[]
  defaults: Record<string, number>
}

export interface LabExperimentResult {
  key: string
  number: number
  title: string
  concept: string
  description: string
  sql: string
  dialect: string
  notes: string[]
  params: Record<string, number>
  statements: LabStep[]
}
