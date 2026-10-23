// Everything the page knows about the backend lives in this file.

export type Status = 'READY' | 'BLOCKED' | 'NEEDS_REVIEW'

export interface Contractor {
  id: string
  name: string
  trade: string | null
}

export interface Assessment {
  job_id: string
  title: string | null
  site: string | null
  start_date: string
  end_date: string
  policy_id: string
  contractors: Contractor[]
  status: Status
  reason: string
  followup_status: string | null
}

export interface ReadinessExplanation {
  job_id: string
  answer: string
}

// FastAPI returns two error shapes:
//   our own checks:     {"detail": "end must be on or after start"}
//   FastAPI validation: {"detail": [{"loc": ["query", "start"], "msg": "..."}]}
function errorMessage(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item: { loc?: unknown[]; msg?: string }) => `${item.loc?.at(-1) ?? 'input'}: ${item.msg}`)
      .join('; ')
  }
  return `Request failed (HTTP ${status})`
}

export interface FollowupDraft {
  id: number
  status: string
  job_id: string
  contractor_id: string
  recipient: string
  subject: string
  body: string
  reason: string
  evidence_ids: string[]
  created_at: string
}

export interface FollowupDelivery {
  delivery_id: number
  draft_id: number
  approval_id: number
  status: 'sending' | 'sent' | 'rejected' | 'unknown' | 'confirmed_not_sent'
  already_processed: boolean
}

export interface CurrentUser {
  issuer: string
  subject: string
  organisation_id: string
  role: 'viewer' | 'manager'
}

export interface CurrentIdentity {
  issuer: string
  subject: string
}

export type LoginState =
  | { status: 'signed_out' }
  | { status: 'signed_in'; user: CurrentUser }
  | { status: 'unprovisioned'; identity: CurrentIdentity }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api${path}`, { credentials: 'same-origin', ...init })
  } catch {
    throw new Error('Cannot reach the API. Is "fastapi dev api.py" running?')
  }

  const body = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status >= 500) {
      // Also what Vite's proxy returns when FastAPI itself is not running.
      throw new Error(
        `The API or database is unavailable (HTTP ${response.status}). ` +
          'Are "fastapi dev api.py" and "docker compose up -d" running?',
      )
    }
    throw new Error(errorMessage(body, response.status))
  }
  return body as T
}

export async function fetchLoginState(): Promise<LoginState> {
  let response: Response
  try {
    response = await fetch('/api/auth/me', { credentials: 'same-origin' })
  } catch {
    throw new Error('Cannot reach the API. Is "fastapi dev api.py" running?')
  }

  if (response.status === 401) return { status: 'signed_out' }
  if (response.status === 403) {
    const identityResponse = await fetch('/api/auth/identity', { credentials: 'same-origin' })
    if (identityResponse.ok) {
      return { status: 'unprovisioned', identity: (await identityResponse.json()) as CurrentIdentity }
    }
  }
  if (response.status >= 500) {
    throw new Error(
      `The API or database is unavailable (HTTP ${response.status}). ` +
        'Are "fastapi dev api.py" and "docker compose up -d" running?',
    )
  }
  const body = await response.json().catch(() => null)
  if (!response.ok) throw new Error(errorMessage(body, response.status))
  return { status: 'signed_in', user: body as CurrentUser }
}

export function logout(): Promise<{ status: string }> {
  return request<{ status: string }>('/auth/logout', { method: 'POST' })
}

export function loginToLocalDemo(): Promise<{ status: string; mode: string }> {
  return request<{ status: string; mode: string }>('/auth/dev-login', { method: 'POST' })
}

export function fetchAssessments(start: string, end: string): Promise<Assessment[]> {
  return request(`/assessments?${new URLSearchParams({ start, end })}`)
}

export function fetchReadinessExplanation(jobId: string): Promise<ReadinessExplanation> {
  return request(`/assessments/${encodeURIComponent(jobId)}/explanation`)
}

// Stores a draft on the server. Nothing is sent to the contractor.
export function createFollowup(jobId: string): Promise<FollowupDraft> {
  return request(`/assessments/${encodeURIComponent(jobId)}/followups`, { method: 'POST' })
}

export function saveFollowup(id: number, subject: string, body: string): Promise<FollowupDraft> {
  return request(`/followups/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject, body }),
  })
}

// Approves the saved text. Editing afterwards returns it to draft.
export function approveFollowup(id: number): Promise<FollowupDraft> {
  return request(`/followups/${id}/approve`, { method: 'POST' })
}

export function sendApprovedFollowup(id: number): Promise<FollowupDelivery> {
  return request(`/followups/${id}/send`, { method: 'POST' })
}

export function reconcileFollowupDelivery(
  id: number,
  outcome: 'sent' | 'not_sent',
  note: string,
): Promise<FollowupDelivery> {
  return request(`/followups/${id}/reconcile`, {
    method: 'POST',
    body: JSON.stringify({ outcome, note }),
  })
}
