/** Application shell: navigation sidebar, top bar and the routed page. */
import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import api from '../services/api'
import {
  IconBuilding,
  IconCalendar,
  IconCard,
  IconDatabase,
  IconDashboard,
  IconMenu,
  IconReport,
  IconTicket,
  IconUsers,
} from './Icons'

interface NavEntry {
  to: string
  label: string
  icon: JSX.Element
}

const PRIMARY: NavEntry[] = [
  { to: '/', label: 'Dashboard', icon: <IconDashboard /> },
  { to: '/events', label: 'Events', icon: <IconCalendar /> },
  { to: '/venues', label: 'Venues', icon: <IconBuilding /> },
  { to: '/organizers', label: 'Organizers', icon: <IconUsers /> },
  { to: '/attendees', label: 'Attendees', icon: <IconUsers /> },
]

const OPERATIONS: NavEntry[] = [
  { to: '/registrations', label: 'Registrations', icon: <IconTicket /> },
  { to: '/payments', label: 'Payments', icon: <IconCard /> },
]

const DATABASE: NavEntry[] = [
  { to: '/reports', label: 'Reports', icon: <IconReport /> },
  { to: '/sql-lab', label: 'SQL Lab', icon: <IconDatabase /> },
]

const TITLES: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Dashboard', subtitle: 'Live metrics calculated by the database' },
  '/events': { title: 'Events', subtitle: 'Create, schedule and monitor every event' },
  '/venues': { title: 'Venues', subtitle: 'Locations, capacities and availability' },
  '/organizers': { title: 'Organizers', subtitle: 'Clubs and teams that run the events' },
  '/attendees': { title: 'Attendees', subtitle: 'Participants and their registration history' },
  '/registrations': { title: 'Registrations', subtitle: 'Enrol attendees and track attendance' },
  '/payments': { title: 'Payments', subtitle: 'Ticket payments, refunds and revenue' },
  '/reports': { title: 'Reports', subtitle: 'Read-only SQL reports with the executed query' },
  '/sql-lab': { title: 'SQL Lab', subtitle: 'The nine DBMS experiments against the live database' },
}

export default function Layout() {
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [health, setHealth] = useState<{ connected: boolean; detail: string }>({
    connected: false,
    detail: 'checking…',
  })

  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        const result = await api.health()
        if (!active) return
        setHealth({
          connected: result.database_connected,
          detail: `${result.dialect ?? 'db'} · ${result.row_counts?.events ?? 0} events`,
        })
      } catch {
        if (active) setHealth({ connected: false, detail: 'database unreachable' })
      }
    }
    check()
    const timer = window.setInterval(check, 30000)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [])

  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname])

  const heading = TITLES[location.pathname] ?? { title: 'EventEase', subtitle: '' }

  const renderNav = (entries: NavEntry[]) =>
    entries.map((entry) => (
      <NavLink
        key={entry.to}
        to={entry.to}
        end={entry.to === '/'}
        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
      >
        {entry.icon}
        {entry.label}
      </NavLink>
    ))

  return (
    <div className="app-shell">
      <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
        <div className="sidebar__brand">
          <div className="sidebar__logo">EE</div>
          <div>
            <h1>EventEase</h1>
            <span>Event Management</span>
          </div>
        </div>

        <nav className="sidebar__nav">
          <div className="nav-label">Overview</div>
          {renderNav(PRIMARY)}
          <div className="nav-label">Operations</div>
          {renderNav(OPERATIONS)}
          <div className="nav-label">Database</div>
          {renderNav(DATABASE)}
        </nav>

        <div className="sidebar__footer">
          <div className="db-status">
            <span className={`db-dot ${health.connected ? '' : 'offline'}`} />
            {health.connected ? 'MySQL connected' : 'Database offline'}
          </div>
          <div style={{ marginTop: 4 }}>{health.detail}</div>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <div className="row">
            <button
              type="button"
              className="btn btn--ghost btn--sm mobile-toggle"
              onClick={() => setMenuOpen((open) => !open)}
              aria-label="Toggle navigation"
            >
              <IconMenu />
            </button>
            <div>
              <h2>{heading.title}</h2>
              <p>{heading.subtitle}</p>
            </div>
          </div>
          <div className="topbar__actions">
            <span className="badge badge--accent">
              <span className="badge-dot" />
              DBMS Mini Project
            </span>
          </div>
        </header>

        <main className="page">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
