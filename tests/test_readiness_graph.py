import readiness_graph


def test_tool_execution_uses_organisation_from_graph_state(monkeypatch):
    calls = []

    def fake_execute_tool(tool_name, tool_input, organisation_id):
        calls.append((tool_name, tool_input, organisation_id))
        return {"is_error": False, "content": "{}"}

    monkeypatch.setattr(readiness_graph, "execute_tool", fake_execute_tool)

    result = readiness_graph.run_tools({
        "messages": [
            {"role": "user", "content": "Explain job"},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tool-1",
                        "name": "get_job_assessment",
                        "input": {"job_id": "JOB-102"},
                    }
                ],
            },
        ],
        "needs_tool": True,
        "answer": "",
        "question": "Explain job",
        "policy_context": [],
        "organisation_id": "ORG-VERIFIED",
    })

    assert calls == [
        ("get_job_assessment", {"job_id": "JOB-102"}, "ORG-VERIFIED")
    ]
    assert result["messages"][-1]["content"][0]["content"] == "{}"
