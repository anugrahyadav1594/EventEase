/** Reports page: every report shows the SQL that produced the result. */
import { useEffect, useState } from 'react'
import api from '../services/api'
import type { ReportResult } from '../types'
import SqlBlock from '../components/SqlBlock'
import { IconChart, IconInfo, IconPlay, IconRefresh } from '../components/Icons'

interface ReportInfo {
  key: string
  title: string
  concept: string
  description: string
  endpoint: string
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportInfo[]>([])
  const [active, setActive] = useState<string>('event-registrations')
  const [result, setResult] = useState<ReportResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listReports()
      .then((items) => {
        setReports(items)
        if (items.length) setActive(items[0].key)
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    if (!active) return
    setLoading(true)
    setError(null)
    api
      .getReport(active)
      .then(setResult)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [active])

  return (
    <>
      <div className="card">
        <div className="card__header">
          <div>
            <h3>Report catalogue</h3>
            <p>Seven read-only reports - the SQL is identical to the statement the backend executed</p>
          </div>
          <button type="button" className="btn btn--ghost btn--sm" onClick={() => active && api.getReport(active).then(setResult)}>
            <IconRefresh width={14} height={14} /> Re-run
          </button>
        </div>
        <div className="tabs" style={{ padding: '0 12px' }}>
          {reports.map((report) => (
            <button
              key={report.key}
              type="button"
              className={`tab ${active === report.key ? 'active' : ''}`}
              onClick={() => setActive(report.key)}
            >
              {report.title}
            </button>
          ))}
        </div>
      </div>

      {error ? <div className="alert alert--error">{error}</div> : null}

      {result ? (
        <div className="stack" style={{ gap: 18 }}>
          <div className="card">
            <div className="card__header">
              <div>
                <h3>{result.title}</h3>
                <p>{result.description}</p>
              </div>
              <span className="concept-pill">{result.concept}</span>
            </div>
            <div className="card__body">
              <div className="row row--between" style={{ marginBottom: 10 }}>
                <strong style={{ fontSize: 13 }}>Executed SQL</strong>
                <span className="badge badge--accent">
                  <IconChart width={13} height={13} /> {result.row_count} row(s)
                </span>
              </div>
              <SqlBlock sql={result.sql} inline />
              <div className="alert alert--info" style={{ marginTop: 14 }}>
                <IconInfo width={16} height={16} />
                <span>{result.explanation}</span>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card__header">
              <h3>Result set</h3>
              <span className="badge badge--accent">{result.row_count} rows</span>
            </div>
            {loading ? (
              <div className="loading-row">
                <span className="spinner" /> Running query…
              </div>
            ) : (
              <div className="table-wrap">
                <table className="data">
                  <thead>
                    <tr>
                      {result.columns.map((column) => (
                        <th key={column}>{column.replace(/_/g, ' ')}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.rows.map((row, index) => (
                      <tr key={index}>
                        {result.columns.map((column) => (
                          <td key={column}>
                            {row[column] === null || row[column] === undefined
                              ? '—'
                              : String(row[column])}
                          </td>
                        ))}
                      </tr>
                    ))}
                    {result.rows.length === 0 ? (
                      <tr>
                        <td colSpan={result.columns.length} className="muted">
                          The query returned no rows.
                        </td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : null}

      {!result && !loading ? (
        <div className="card">
          <div className="card__body">
            <div className="empty">
              <strong>
                <IconPlay width={16} height={16} /> Select a report
              </strong>
              Choose one of the reports above - the SQL is executed against the live database.
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
