import { Fragment, useMemo, useState, type FormEvent } from 'react'
import {
  createFollowup,
  fetchAssessments,
  saveFollowup,
  type Assessment,
  type FollowupDraft,
  type Status,
} from './api'

// Four weeks of the demo period (the API allows up to 31 days).
const DEFAULT_START = '2026-10-05'
const DEFAULT_END = '2026-11-01'

const STATUSES: Status[] = ['READY', 'NEEDS_REVIEW', 'BLOCKED']

const STATUS_LABELS: Record<Status, string> = {
  READY: 'Ready',
  BLOCKED: 'Blocked',
  NEEDS_REVIEW: 'Needs review',
}

const REASON_LABELS: Record<string, string> = {
  REQUIREMENTS_MET: 'All required documents are valid',
  EXPIRES_BEFORE_JOB_END: 'A document expires before the job ends',
  NOT_VALID_AT_JOB_START: 'A document is not yet valid when the job starts',
  MISSING_DOCUMENT: 'A required document is missing',
  INSUFFICIENT_COVERAGE: 'Insurance coverage is below the policy minimum',
  UNVERIFIED_DOCUMENT: 'A document has not been verified yet',
}

// The only finding the server can draft a follow-up for so far.
const canDraftFollowup = (a: Assessment) =>
  a.status === 'BLOCKED' && a.reason === 'EXPIRES_BEFORE_JOB_END' && a.contractors.length === 1

// The screen is always in exactly one of these states.
type View =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'results'; assessments: Assessment[] }

export default function App() {
  const [start, setStart] = useState(DEFAULT_START)
  const [end, setEnd] = useState(DEFAULT_END)
  const [view, setView] = useState<View>({ kind: 'idle' })

  async function checkJobs(event: FormEvent) {
    event.preventDefault()
    setView({ kind: 'loading' })
    try {
      setView({ kind: 'results', assessments: await fetchAssessments(start, end) })
    } catch (error) {
      setView({ kind: 'error', message: (error as Error).message })
    }
  }

  return (
    <main>
      <header>
        <h1>Contractor readiness</h1>
        <p className="subtitle">Synthetic demo data · Demo Field Services</p>
      </header>

      <form onSubmit={checkJobs}>
        <label>
          From
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} required />
        </label>
        <label>
          To
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} required />
        </label>
        <button type="submit" disabled={view.kind === 'loading'}>
          {view.kind === 'loading' ? 'Checking…' : 'Check jobs'}
        </button>
      </form>

      <section aria-live="polite">
        {view.kind === 'idle' && <p className="hint">Choose dates and check which jobs are ready.</p>}
        {view.kind === 'loading' && <p className="hint">Checking jobs…</p>}
        {view.kind === 'error' && (
          <p className="error" role="alert">
            {view.message}
          </p>
        )}
        {view.kind === 'results' && <Results assessments={view.assessments} />}
      </section>
    </main>
  )
}

function Results({ assessments }: { assessments: Assessment[] }) {
  const [statusFilter, setStatusFilter] = useState<Status | null>(null)
  const [search, setSearch] = useState('')
  const [followupJobId, setFollowupJobId] = useState<string | null>(null)

  const counts = useMemo(() => {
    const result: Record<Status, number> = { READY: 0, NEEDS_REVIEW: 0, BLOCKED: 0 }
    for (const assessment of assessments) result[assessment.status] += 1
    return result
  }, [assessments])

  const visible = useMemo(() => {
    const term = search.trim().toLowerCase()
    return assessments.filter((a) => {
      if (statusFilter && a.status !== statusFilter) return false
      if (!term) return true
      const text = [a.job_id, a.title, a.site, ...a.contractors.map((c) => c.name)].join(' ').toLowerCase()
      return text.includes(term)
    })
  }, [assessments, statusFilter, search])

  if (assessments.length === 0) {
    return <p className="hint">No jobs in this date range.</p>
  }

  return (
    <>
      <div className="summary">
        {STATUSES.map((status) => (
          <button
            key={status}
            type="button"
            className={`card ${status.toLowerCase()}`}
            aria-pressed={statusFilter === status}
            onClick={() => setStatusFilter(statusFilter === status ? null : status)}
          >
            <span className="count">{counts[status]}</span>
            <span className="label">{STATUS_LABELS[status]}</span>
          </button>
        ))}
      </div>

      <div className="toolbar">
        <input
          type="search"
          placeholder="Search job, site or contractor"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search jobs"
        />
        <span className="hint">
          {visible.length} of {assessments.length} jobs
          {statusFilter && (
            <>
              {' · '}
              <button type="button" className="link" onClick={() => setStatusFilter(null)}>
                show all
              </button>
            </>
          )}
        </span>
      </div>

      {visible.length === 0 ? (
        <p className="hint">No jobs match these filters.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Job</th>
                <th>Dates</th>
                <th>Contractor</th>
                <th>Status</th>
                <th>Reason</th>
                <th>
                  <span className="visually-hidden">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {visible.map((a) => (
                <Fragment key={a.job_id}>
                  <tr>
                    <td>
                      <div className="primary">{a.title ?? a.job_id}</div>
                      <div className="secondary">
                        {a.job_id}
                        {a.site && ` · ${a.site}`}
                        {a.policy_id.includes('HIGH-RISK') && <span className="tag">High risk</span>}
                      </div>
                    </td>
                    <td className="nowrap">{formatRange(a.start_date, a.end_date)}</td>
                    <td>
                      {a.contractors.map((c) => (
                        <div key={c.id}>
                          {c.name}
                          <span className="secondary"> · {c.id}</span>
                        </div>
                      ))}
                    </td>
                    <td>
                      <span className={`badge ${a.status.toLowerCase()}`}>{STATUS_LABELS[a.status] ?? a.status}</span>
                    </td>
                    <td>
                      {REASON_LABELS[a.reason] ?? a.reason}
                      <code>{a.reason}</code>
                    </td>
                    <td>
                      {canDraftFollowup(a) && (
                        <button
                          type="button"
                          className="secondary-button"
                          aria-expanded={followupJobId === a.job_id}
                          onClick={() => setFollowupJobId(followupJobId === a.job_id ? null : a.job_id)}
                        >
                          {followupJobId === a.job_id ? 'Close' : 'Draft follow-up'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {followupJobId === a.job_id && (
                    <tr className="followup-row">
                      <td colSpan={6}>
                        <FollowupPanel jobId={a.job_id} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

type DraftView =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; draft: FollowupDraft }

function FollowupPanel({ jobId }: { jobId: string }) {
  const [view, setView] = useState<DraftView>({ kind: 'idle' })
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  function show(draft: FollowupDraft) {
    setView({ kind: 'ready', draft })
    setSubject(draft.subject)
    setBody(draft.body)
  }

  async function prepare() {
    setView({ kind: 'loading' })
    try {
      show(await createFollowup(jobId))
    } catch (error) {
      setView({ kind: 'error', message: (error as Error).message })
    }
  }

  async function save(event: FormEvent, draft: FollowupDraft) {
    event.preventDefault()
    setSaving(true)
    setSaveMessage(null)
    try {
      show(await saveFollowup(draft.id, subject, body))
      setSaveMessage('Saved.')
    } catch (error) {
      setSaveMessage((error as Error).message)
    } finally {
      setSaving(false)
    }
  }

  if (view.kind !== 'ready') {
    return (
      <div className="followup">
        <p className="hint">
          Prepare a message asking the contractor for insurance evidence that covers the whole job. It is stored as
          a draft; nothing is sent.
        </p>
        <button type="button" onClick={prepare} disabled={view.kind === 'loading'}>
          {view.kind === 'loading' ? 'Preparing…' : 'Prepare draft'}
        </button>
        {view.kind === 'error' && (
          <p className="error" role="alert">
            {view.message}
          </p>
        )}
      </div>
    )
  }

  const { draft } = view
  const changed = subject !== draft.subject || body !== draft.body

  return (
    <form className="followup" onSubmit={(e) => save(e, draft)}>
      <p className="notice">Draft #{draft.id} · not sent. Sending will need approval in a later step.</p>
      <dl>
        <dt>To</dt>
        <dd>
          {draft.recipient} <span className="secondary">· {draft.contractor_id}</span>
        </dd>
        <dt>Evidence</dt>
        <dd>{draft.evidence_ids.join(', ')}</dd>
      </dl>
      <label>
        Subject
        <input value={subject} onChange={(e) => setSubject(e.target.value)} required maxLength={200} />
      </label>
      <label>
        Message
        <textarea value={body} onChange={(e) => setBody(e.target.value)} required maxLength={5000} rows={12} />
      </label>
      <div className="followup-actions">
        <button type="submit" disabled={saving || !changed}>
          {saving ? 'Saving…' : 'Save draft'}
        </button>
        {saveMessage && <span className="hint" role="status">{saveMessage}</span>}
      </div>
    </form>
  )
}

// Dates are calendar days, so format them in UTC to avoid time-zone shifts.
const dayFormat = new Intl.DateTimeFormat('en-AU', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' })

function formatRange(start: string, end: string): string {
  const first = dayFormat.format(new Date(`${start}T00:00:00Z`))
  return start === end ? first : `${first} – ${dayFormat.format(new Date(`${end}T00:00:00Z`))}`
}
