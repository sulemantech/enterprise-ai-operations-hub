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

export async function fetchAssessments(start: string, end: string): Promise<Assessment[]> {
  let response: Response
  try {
    response = await fetch(`/api/assessments?${new URLSearchParams({ start, end })}`)
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
  return body as Assessment[]
}
