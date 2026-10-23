/** Router of the EventEase dashboard. */
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { ToastProvider } from './components/Toast'
import AttendeesPage from './pages/AttendeesPage'
import DashboardPage from './pages/DashboardPage'
import EventsPage from './pages/EventsPage'
import OrganizersPage from './pages/OrganizersPage'
import PaymentsPage from './pages/PaymentsPage'
import RegistrationsPage from './pages/RegistrationsPage'
import ReportsPage from './pages/ReportsPage'
import SqlLabPage from './pages/SqlLabPage'
import VenuesPage from './pages/VenuesPage'

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="events" element={<EventsPage />} />
          <Route path="venues" element={<VenuesPage />} />
          <Route path="organizers" element={<OrganizersPage />} />
          <Route path="attendees" element={<AttendeesPage />} />
          <Route path="registrations" element={<RegistrationsPage />} />
          <Route path="payments" element={<PaymentsPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="sql-lab" element={<SqlLabPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </ToastProvider>
  )
}
