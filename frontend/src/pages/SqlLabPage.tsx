/** SQL Lab: runs the nine DBMS experiments against the live database. */
import { useEffect, useState } from 'react'
import api from '../services/api'
import type { LabExperimentResult, LabExperimentSummary } from '../types'
import SqlBlock from '../components/SqlBlock'
import { IconInfo, IconPlay, IconRefresh } from '../components/Icons'

const PARAM_LABELS: Record<string, string> = {
  threshold: 'Minimum registrations per event',
  min_events: 'Minimum events per organizer',
  venue_threshold: 'Minimum events per venue',
}

export default function SqlLabPage() {
  const [experiments, setExperiments] = useState<LabExperimentSummary[]>([])
  const [active, setActive] = useState<string>('ddl-dml')
  const [result, setResult] = useState<LabExperimentResult | null>(null)
  const [params, setParams] = useState<Record<string, number>>({})
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listExperiments()
      .then((items) => {
        setExperiments(items)
        const first = items[0]
        if (first) {
          setActive(first.key)
          setParams(first.defaults ?? {})
        }
      })
      .catch((err) => setError(err.message))
  }, [])

  const select = (experiment: LabExperimentSummary) => {
    setActive(experiment.key)
    setParams(experiment.defaults ?? {})
    setResult(null)
  }

  const run = async () => {
    setRunning(true)
    setError(null)
    try {
      const response = await api.runExperiment(active, params)
      setResult(response)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  const current = experiments.find((item) => item.key === active)

  return (
    <div className="lab-layout">
      <div className="card">
        <div className="card__header">
          <h3>Experiments</h3>
          <span className="badge badge--accent">9</span>
        </div>
        <div className="card__body">
          <div className="lab-nav">
            {experiments.map((experiment) => (
              <button
                key={experiment.key}
                type="button"
                className={`lab-nav__item ${active === experiment.key ? 'active' : ''}`}
                onClick={() => select(experiment)}
              >
                <div className="lab-nav__number">EXPERIMENT {experiment.number}</div>
                <div className="lab-nav__title">{experiment.title}</div>
                <div className="lab-nav__concept">{experiment.concept}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="stack" style={{ gap: 18 }}>
        <div className="card">
          <div className="card__header">
            <div>
              <h3>{current?.title ?? 'Experiment'}</h3>
              <p>{current?.description}</p>
            </div>
            <span className="concept-pill">{current?.concept}</span>
          </div>
          <div className="card__body">
            {current && Object.keys(current.defaults ?? {}).length > 0 ? (
              <div className="filters" style={{ marginBottom: 14 }}>
                {Object.entries(current.defaults ?? {}).map(([name, value]) => (
                  <div className="field" key={name}>
                    <label>{PARAM_LABELS[name] ?? name}</label>
                    <input
                      type="number"
                      min={0}
                      value={params[name] ?? value}
                      onChange={(event) => setParams({ ...params, [name]: Number(event.target.value) })}
                      style={{ width: 110 }}
                    />
                  </div>
                ))}
              </div>
            ) : null}

            <div className="row" style={{ marginBottom: 14 }}>
              <button type="button" className="btn btn--primary" onClick={run} disabled={running}>
                <IconPlay width={15} height={15} /> {running ? 'Running…' : 'Run experiment'}
              </button>
              {result ? (
                <button type="button" className="btn btn--ghost" onClick={run}>
                  <IconRefresh width={14} height={14} /> Run again
                </button>
              ) : null}
              <span className="muted">
                {result ? `${result.statements.length} statement(s) executed on the ${result.dialect} server` : 'No SQL has been executed yet.'}
              </span>
            </div>

            {current?.notes?.length ? (
              <ul className="muted" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.8 }}>
                {current.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            ) : null}

            {error ? (
              <div className="alert alert--error" style={{ marginTop: 12 }}>
                {error}
              </div>
            ) : null}
          </div>
        </div>

        {result?.notes?.length ? (
          <div className="alert alert--info">
            <IconInfo width={16} height={16} />
            <span>{result.notes[result.notes.length - 1]}</span>
          </div>
        ) : null}

        {result ? (
          <div className="steps">
            {result.statements.map((step, index) => (
              <div key={index} className={`step ${step.status === 'error' ? 'step--error' : ''}`}>
                <div className="step__head">
                  <div>
                    <div className="step__label">
                      {index + 1}. {step.label}
                    </div>
                    {step.note ? <div className="step__note">{step.note}</div> : null}
                  </div>
                  <span className={`badge badge--${step.status === 'error' ? 'danger' : 'success'}`}>
                    <span className="badge-dot" />
                    {step.status === 'error' ? 'rejected by the database' : `${step.row_count} row(s)`}
                  </span>
                </div>
                <div className="step__body">
                  <SqlBlock sql={step.sql} inline />
                  {step.status === 'error' ? (
                    <div className="alert alert--error" style={{ marginTop: 12 }}>
                      {step.message}
                    </div>
                  ) : null}
                  {step.rows.length > 0 ? (
                    <div className="table-wrap" style={{ marginTop: 12 }}>
                      <table className="data">
                        <thead>
                          <tr>
                            {step.columns.map((column) => (
                              <th key={column}>{column.replace(/_/g, ' ')}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {step.rows.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                              {step.columns.map((column) => (
                                <td key={column}>
                                  {row[column] === null || row[column] === undefined ? '—' : String(row[column])}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}
