from citation_validation import unsupported_citations

policy_context = [{
    "job_id": "JOB-102",
    "passages": [{
        "document_id": "PROC-CONTRACTOR-001",
        "document_version": 2,
        "section_id": "CP-03",
    }],
}]

valid_answer = "Insurance must cover the job [PROC-CONTRACTOR-001 v2, CP-03]."
assert unsupported_citations(valid_answer, policy_context) == set()
print("Valid citation check passed.")

invalid_answer = "Insurance is sufficient [PROC-CONTRACTOR-001 v2, CP-99]."
assert unsupported_citations(invalid_answer, policy_context) == {
    "[PROC-CONTRACTOR-001 v2, CP-99]"
}
print("Unsupported citation check passed.")

assert unsupported_citations(valid_answer, []) == {
    "[PROC-CONTRACTOR-001 v2, CP-03]"
}
print("Citation without sources check passed.")