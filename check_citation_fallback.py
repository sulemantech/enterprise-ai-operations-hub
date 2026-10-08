import json
from types import SimpleNamespace
from unittest.mock import patch

from readiness_graph import explain_assessment

assessment = {
    "job": {"id": "JOB-102"},
    "status": "BLOCKED",
    "reason": "EXPIRES_BEFORE_JOB_END",
}

state = {
    "messages": [{
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "test-1",
            "is_error": False,
            "content": json.dumps(assessment),
        }],
    }],
    "policy_context": [{
        "job_id": "JOB-102",
        "tool_use_id": "test-1",
        "passages": [{
            "document_id": "PROC-CONTRACTOR-001",
            "document_version": 2,
            "section_id": "CP-03",
        }],
    }],
}

fake_response = SimpleNamespace(
    stop_reason="end_turn",
    content=[SimpleNamespace(
        type="text",
        text="The job is ready [PROC-CONTRACTOR-001 v2, CP-99].",
    )],
)

with patch("readiness_graph.anthropic.Anthropic"), patch(
    "readiness_graph.call_model",
    return_value=fake_response,
):
    result = explain_assessment(state)

answer = result["answer"]
assert "JOB-102: BLOCKED / EXPIRES_BEFORE_JOB_END." in answer
assert "CP-99" not in answer
assert "The job is ready" not in answer
assert "citations failed validation" in answer
assert result["messages"][-1]["content"] == [
    {"type": "text", "text": answer}
]

print("Citation fallback check passed.")

valid_text = (
    "JOB-102 is BLOCKED / EXPIRES_BEFORE_JOB_END. "
    "Evidence must cover the full job period "
    "[PROC-CONTRACTOR-001 v2, CP-03]."
)
fake_response.content[0].text = valid_text

with patch("readiness_graph.anthropic.Anthropic"), patch(
    "readiness_graph.call_model",
    return_value=fake_response,
):
    result = explain_assessment(state)

assert result["answer"] == valid_text
assert result["messages"][-1]["content"] == [
    {"type": "text", "text": valid_text}
]

print("Allowed citation passes through unchanged.")