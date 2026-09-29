"""Ask Claude to explain a readiness result that the rules already decided.

Claude explains; it never decides. The status and reason come from
readiness.py, and check_grounding() verifies the explanation against the
same facts before anyone sees it.

Usage: python explain.py JOB-102
"""

import json
import re
import sys

import anthropic
from pydantic import BaseModel, ConfigDict

import repository
from db import get_engine  # also loads .env, which holds ANTHROPIC_API_KEY
from readiness import assess_job

MODEL = "claude-opus-5"

SYSTEM_PROMPT = """\
You explain contractor readiness results to an operations manager.

A rules engine has already decided the status and reason. Do not re-decide them:
copy them exactly into your answer.

Use only the facts in the user message. Never add requirements, dates, amounts,
or documents that are not there.

In the explanation, write 2-3 plain sentences: what the problem is (or that there
is none), which document and dates cause it, and what would resolve it.
In document_ids, list the IDs of the documents your explanation refers to.
Use an empty list when no document exists, for example a missing licence.
"""


class Explanation(BaseModel):
    # extra="forbid" puts additionalProperties: false in the JSON schema,
    # which structured outputs require.
    model_config = ConfigDict(extra="forbid")

    status: str
    reason: str
    document_ids: list[str]
    explanation: str


def build_facts(job: dict, documents: list[dict], policy: dict, status: str, reason: str) -> dict:
    """Everything Claude may use, and nothing else."""
    return {
        "job": job,
        "policy": policy,
        "contractor_documents": documents,
        "rules_engine_result": {"status": status, "reason": reason},
    }


def ask_claude(client: anthropic.Anthropic, facts: dict) -> Explanation:
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(facts, indent=2)}],
        output_config={
            "effort": "low",  # A short explanation doesn't need deep reasoning.
            "format": {"type": "json_schema", "schema": Explanation.model_json_schema()},
        },
        # If a safety classifier declines, retry server-side on Anthropic's recommended fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )

    usage = response.usage
    print(f"[{response.model}: {usage.input_tokens} in / {usage.output_tokens} out tokens]")

    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to answer")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Claude's answer was cut off (max_tokens reached)")

    text = next(block.text for block in response.content if block.type == "text")
    # The schema constrains Claude's output; validating again here means our code
    # never trusts the shape of model output blindly.
    return Explanation.model_validate_json(text)


def check_grounding(explanation: Explanation, facts: dict) -> list[str]:
    """Return every way the explanation disagrees with the facts (empty = grounded)."""
    problems = []

    expected = facts["rules_engine_result"]
    if (explanation.status, explanation.reason) != (expected["status"], expected["reason"]):
        problems.append(
            f"says {explanation.status}/{explanation.reason}, "
            f"rules decided {expected['status']}/{expected['reason']}"
        )

    known_ids = {facts["job"]["id"], *facts["job"]["contractor_ids"]}
    known_ids |= {document["id"] for document in facts["contractor_documents"]}
    mentioned = set(explanation.document_ids)
    mentioned |= set(re.findall(r"\b(?:DOC|JOB|CON)-\d+\b", explanation.explanation))
    for unknown in sorted(mentioned - known_ids):
        problems.append(f"refers to {unknown}, which is not in the facts")

    return problems


def explain_job(job_id: str) -> None:
    with get_engine().connect() as connection:
        job = repository.get_job(connection, job_id)
        if job is None:
            sys.exit(f"Job {job_id} not found")
        documents = repository.documents_for(connection, job["contractor_ids"])
        policy = repository.get_policy(connection, job["policy_id"], job["policy_version"])

    status, reason = assess_job(job, documents, policy)
    facts = build_facts(job, documents, policy, status, reason)
    explanation = ask_claude(anthropic.Anthropic(), facts)

    print(f"\n{job_id}: {status} / {reason}  (from the rules)")
    print(f"\n{explanation.explanation}")
    print(f"\nDocuments cited: {explanation.document_ids or 'none'}")

    problems = check_grounding(explanation, facts)
    if problems:
        print("\nNOT GROUNDED - do not show this explanation:")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("\nGrounding check passed.")


if __name__ == "__main__":
    explain_job(sys.argv[1] if len(sys.argv) > 1 else "JOB-102")
