import { Fragment, useEffect, useMemo, useState, type FormEvent } from 'react'
import {
  approveFollowup,
  createFollowup,
  fetchLoginState,
  fetchAssessments,
  fetchReadinessExplanation,
  loginToLocalDemo,
  logout,
  sendApprovedFollowup,
  saveFollowup,
  type Assessment,
  type FollowupDraft,
  type LoginState,
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

const FOLLOWUP_STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  approved: 'Approved',
  sending: 'Sending',
  sent: 'Sent to test workflow',
  delivery_rejected: 'Rejected',
  delivery_unknown: 'Unknown · reconcile first',
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
  const [loginState, setLoginState] = useState<LoginState | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)
  const [start, setStart] = useState(DEFAULT_START)
  const [end, setEnd] = useState(DEFAULT_END)
  const [view, setView] = useState<View>({ kind: 'idle' })

  async function refreshLoginState() {
    setAuthError(null)
    try {
      setLoginState(await fetchLoginState())
    } catch (error) {
      setAuthError((error as Error).message)
    }
  }

  useEffect(() => {
    void refreshLoginState()
  }, [])

  async function signOut() {
    try {
      await logout()
      setLoginState({ status: 'signed_out' })
    } catch (error) {
      setAuthError((error as Error).message)
    }
  }

  async function signIn() {
    if (!import.meta.env.DEV) {
      window.location.assign('/api/auth/login')
      return
    }
    try {
      await loginToLocalDemo()
      await refreshLoginState()
    } catch (error) {
      setAuthError((error as Error).message)
    }
  }

  async function checkJobs(event: FormEvent) {
    event.preventDefault()
    setView({ kind: 'loading' })
    try {
      setView({ kind: 'results', assessments: await fetchAssessments(start, end) })
    } catch (error) {
      setView({ kind: 'error', message: (error as Error).message })
    }
  }

  if (authError) {
    return (
      <main>
        <h1>Sign-in unavailable</h1>
        <p className="error" role="alert">{authError}</p>
        <button type="button" onClick={() => void refreshLoginState()}>Try again</button>
      </main>
    )
  }

  if (!loginState) {
    return <main><p className="hint">Checking your sign-in…</p></main>
  }

  if (loginState.status === 'signed_out') {
    return (
      <main>
        <header>
          <h1>Contractor readiness</h1>
          <p className="subtitle">{import.meta.env.DEV ? 'Open the local demo to review evidence and follow-ups.' : 'Sign in to review evidence and follow-ups.'}</p>
        </header>
        <button type="button" onClick={() => void signIn()}>
          {import.meta.env.DEV ? 'Enter local demo' : 'Sign in with Hellō'}
        </button>
      </main>
    )
  }

  if (loginState.status === 'unprovisioned') {
    return (
      <main>
        <h1>Organisation access not set up</h1>
        <p className="hint">Hellō verified your identity, but an administrator must assign an organisation and role.</p>
        <p>Issuer: <code>{loginState.identity.issuer}</code></p>
        <p>Subject: <code>{loginState.identity.subject}</code></p>
        <button type="button" onClick={() => void refreshLoginState()}>Check access again</button>
        <button type="button" onClick={() => void signOut()}>Sign out</button>
      </main>
    )
  }

  return (
    <main>
      <header>
        <h1>Contractor readiness</h1>
        <p className="subtitle">Synthetic demo data · Demo Field Services</p>
        <p className="subtitle">Signed in as {loginState.user.role}</p>
        <button type="button" onClick={() => void signOut()}>Sign out</button>
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
  const [explanationJobId, setExplanationJobId] = useState<string | null>(null)
  const [explanation, setExplanation] = useState<{ jobId: string; text?: string; error?: string } | null>(null)
  const [followupStatuses, setFollowupStatuses] = useState<Record<string, string>>({})

  function updateFollowupStatus(jobId: string, status: string) {
    setFollowupStatuses((current) => ({ ...current, [jobId]: status }))
  }

  async function explainJob(jobId: string) {
    setExplanationJobId(jobId)
    setExplanation({ jobId })
    try {
      const result = await fetchReadinessExplanation(jobId)
      setExplanation({ jobId, text: result.answer })
    } catch (error) {
      setExplanation({ jobId, error: (error as Error).message })
    } finally {
      setExplanationJobId(null)
    }
  }

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
                <th>Follow-up</th>
                <th>
                  <span className="visually-hidden">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {visible.map((a) => {
                const followupStatus = followupStatuses[a.job_id] ?? a.followup_status
                const deliveryUncertain = followupStatus === 'sending' || followupStatus === 'delivery_unknown'
                return (
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
                      {followupStatus ? (
                        <span className={`followup-status ${followupStatus}`}>
                          {FOLLOWUP_STATUS_LABELS[followupStatus] ?? followupStatus}
                        </span>
                      ) : canDraftFollowup(a) ? (
                        <span className="secondary">Not started</span>
                      ) : (
                        <span className="secondary">—</span>
                      )}
                    </td>
                    <td>
                      <button
                        type="button"
                        className="secondary-button"
                        disabled={explanationJobId === a.job_id}
                        onClick={() => void explainJob(a.job_id)}
                      >
                        {explanationJobId === a.job_id ? 'Explaining…' : 'Explain'}
                      </button>
                      {canDraftFollowup(a) && (
                        <button
                          type="button"
                          className="secondary-button"
                          disabled={deliveryUncertain}
                          title={deliveryUncertain ? 'Check the delivery outcome before creating another draft' : undefined}
                          aria-expanded={followupJobId === a.job_id}
                          onClick={() => setFollowupJobId(followupJobId === a.job_id ? null : a.job_id)}
                        >
                          {followupJobId === a.job_id ? 'Close' : followupStatus ? 'New follow-up' : 'Draft follow-up'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {explanation?.jobId === a.job_id && (
                    <tr className="followup-row">
                      <td colSpan={7}>
                        <p className={explanation.error ? 'error' : 'hint'} role="status">
                          {explanation.error ?? explanation.text ?? 'Preparing an evidence-backed explanation…'}
                        </p>
                      </td>
                    </tr>
                  )}
                  {followupJobId === a.job_id && (
                    <tr className="followup-row">
                      <td colSpan={7}>
                        <FollowupPanel jobId={a.job_id} onStatusChange={updateFollowupStatus} />
                      </td>
                    </tr>
                  )}
                  </Fragment>
                )
              })}
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

function FollowupPanel({ jobId, onStatusChange }: { jobId: string; onStatusChange: (jobId: string, status: string) => void }) {
  const [view, setView] = useState<DraftView>({ kind: 'idle' })
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  function show(draft: FollowupDraft) {
    setView({ kind: 'ready', draft })
    setSubject(draft.subject)
    setBody(draft.body)
    onStatusChange(jobId, draft.status)
  }

  async function prepare() {
    setView({ kind: 'loading' })
    try {
      show(await createFollowup(jobId))
    } catch (error) {
      setView({ kind: 'error', message: (error as Error).message })
    }
  }

  async function approve(draft: FollowupDraft) {
    setSaving(true)
    setSaveMessage(null)
    try {
      show(await approveFollowup(draft.id))
      setSaveMessage('Approved.')
    } catch (error) {
      setSaveMessage((error as Error).message)
    } finally {
      setSaving(false)
    }
  }

  async function send(draft: FollowupDraft) {
    setSaving(true)
    setSaveMessage(null)
    try {
      const outcome = await sendApprovedFollowup(draft.id)
      const status = outcome.status === 'rejected'
        ? 'delivery_rejected'
        : outcome.status === 'unknown'
          ? 'delivery_unknown'
          : outcome.status
      show({ ...draft, status })
      setSaveMessage(
        outcome.already_processed
          ? `This approval was already processed: ${outcome.status}.`
          : outcome.status === 'sent'
            ? 'Sent to the configured test workflow.'
            : outcome.status === 'unknown'
              ? 'Delivery outcome is unknown. Do not retry; reconcile the n8n execution first.'
              : outcome.status === 'rejected'
                ? 'n8n rejected this test delivery.'
                : 'Delivery request is in progress.',
      )
    } catch (error) {
      setSaveMessage((error as Error).message)
    } finally {
      setSaving(false)
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
      <p className="notice">
        {draft.status === 'approved'
          ? `Message #${draft.id} · approved, not sent yet. Editing it will need approval again.`
          : draft.status === 'sent'
            ? `Message #${draft.id} · sent to the configured test workflow.`
            : draft.status === 'sending'
              ? `Message #${draft.id} · delivery is in progress; do not submit it again.`
              : draft.status === 'delivery_unknown'
                ? `Message #${draft.id} · delivery outcome unknown; reconcile before any retry.`
                : draft.status === 'delivery_rejected'
                  ? `Message #${draft.id} · rejected by the test workflow.`
                  : `Draft #${draft.id} · not sent. Approve it before it can be sent.`}
      </p>
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
        {/* Approval applies to the saved text, so unsaved edits must be saved first. */}
        {draft.status === 'draft' && (
          <button
            type="button"
            className="secondary-button"
            disabled={saving || changed}
            title={changed ? 'Save your edits before approving' : undefined}
            onClick={() => approve(draft)}
          >
            Approve
          </button>
        )}
        {draft.status === 'approved' && (
          <button
            type="button"
            className="secondary-button"
            disabled={saving}
            onClick={() => void send(draft)}
          >
            {saving ? 'Sending…' : 'Send to test workflow'}
          </button>
        )}
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
