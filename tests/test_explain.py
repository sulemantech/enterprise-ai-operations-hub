"""The grounding check must reject explanations that disagree with the facts.

These tests use hand-written explanations, so they never call the Claude API.
"""

from explain import Explanation, build_facts, check_grounding
from readiness import load_demo

DEMO = load_demo()
JOB_102 = next(job for job in DEMO["jobs"] if job["id"] == "JOB-102")
CON_002_DOCUMENTS = [d for d in DEMO["documents"] if d["contractor_id"] == "CON-002"]
FACTS = build_facts(JOB_102, CON_002_DOCUMENTS, DEMO["policy"], "BLOCKED", "EXPIRES_BEFORE_JOB_END")


def explanation(**changes) -> Explanation:
    good = {
        "status": "BLOCKED",
        "reason": "EXPIRES_BEFORE_JOB_END",
        "document_ids": ["DOC-003"],
        "explanation": "DOC-003 expires on 2026-10-07, before the job ends on 2026-10-09.",
    }
    return Explanation(**{**good, **changes})


def test_faithful_explanation_passes():
    assert check_grounding(explanation(), FACTS) == []


def test_changed_status_is_caught():
    problems = check_grounding(explanation(status="READY", reason="REQUIREMENTS_MET"), FACTS)

    assert problems == ["says READY/REQUIREMENTS_MET, rules decided BLOCKED/EXPIRES_BEFORE_JOB_END"]


def test_invented_document_id_is_caught():
    assert check_grounding(explanation(document_ids=["DOC-999"]), FACTS) == [
        "refers to DOC-999, which is not in the facts"
    ]


def test_invented_document_in_text_is_caught():
    # DOC-001 exists, but belongs to another contractor, so it is not in this job's facts.
    text = "DOC-003 expires early; DOC-001 could be used instead."

    assert check_grounding(explanation(explanation=text), FACTS) == [
        "refers to DOC-001, which is not in the facts"
    ]
