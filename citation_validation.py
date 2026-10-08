import re


def allowed_citations(policy_context: list[dict]) -> set[str]:
    citations = set()
    for policy in policy_context:
        for passage in policy["passages"]:
            citation = (
                f"[{passage['document_id']} "
                f"v{passage['document_version']}, "
                f"{passage['section_id']}]"
            )
            citations.add(citation)
    return citations

def find_citations(answer: str) -> set[str]:
    return set(
        re.findall(r"\[[^\[\]\n]+ v\d+, [^\[\]\n]+\]", answer)
    )

def unsupported_citations(
    answer: str,
    policy_context: list[dict],
) -> set[str]:
    allowed = allowed_citations(policy_context)
    found = find_citations(answer)
    return found - allowed