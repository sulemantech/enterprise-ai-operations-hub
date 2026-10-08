import json
from unittest.mock import patch

from readiness_graph import retrieve_policy

assessment = {"job": {"id": "JOB-102"}}

state = {
    "question": "Why is JOB-102 blocked?",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "test-tool-1",
            "is_error": False,
            "content": json.dumps(assessment),
        }],
    }],
}

with patch(
    "readiness_graph.retrieve_policy_passages",
    side_effect=TimeoutError("Simulated timeout"),
):
    result = retrieve_policy(state)

context = result["policy_context"][0]
assert context["job_id"] == "JOB-102"
assert context["passages"] == []
assert context["retrieval_status"] == "unavailable"

print("Retrieval failure check passed.")

with patch(
    "readiness_graph.retrieve_policy_passages",
    return_value=[],
):
    result = retrieve_policy(state)

context = result["policy_context"][0]
assert context["passages"] == []
assert context["retrieval_status"] == "no_matching_source"

print("Empty retrieval check passed.")

error_state = {
    "question": "Is JOB-9999 ready?",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "test-missing-job",
            "is_error": True,
            "content": "Job JOB-9999 not found",
        }],
    }],
}

with patch("readiness_graph.retrieve_policy_passages") as mock_retrieve:
    result = retrieve_policy(error_state)

    mock_retrieve.assert_not_called()
    assert result["policy_context"] == []

print("Failed assessment skips retrieval check passed.")