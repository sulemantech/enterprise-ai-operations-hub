from db import get_engine
from embeddings import embed_text, EMBEDDING_MODEL
from knowledge_repository import search_chunks

POLICY_SOURCES = {
    ("ORG-DEMO", "DEMO-CONTRACTOR-001", 1): {
        "document_id": "PROC-CONTRACTOR-001",
        "document_version": 2,
    },
}

def retrieve_policy_passages(question: str, assessment: dict) -> list[dict]:
    """Return the most relevant passages for a given question and assessment."""
    organisation_id = assessment["job"]["organisation_id"]
    policy_id = assessment["job"]["policy_id"]
    policy_version = assessment["job"]["policy_version"]

    source_info = POLICY_SOURCES.get((organisation_id, policy_id, policy_version))
    if source_info is None:
        return []

    reason_text = assessment["reason"].replace("_", " ")
    search_text = f"{question}\nAssessment reason: {reason_text}"

    query_vector = embed_text(search_text, input_type="query")

    with get_engine().connect() as connection:
        matches = search_chunks(
            connection=connection,
            query_vector=query_vector,
            organisation_id=organisation_id,
            policy_id=policy_id,
            policy_version=policy_version,
            document_id=source_info["document_id"],
            document_version=source_info["document_version"],
            embedding_model=EMBEDDING_MODEL,
            limit=3,
        )

    return matches