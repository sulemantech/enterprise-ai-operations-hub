import sys

from db import get_engine
from embeddings import embed_text, EMBEDDING_MODEL
from knowledge_repository import search_chunks


if __name__ == "__main__":
    question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Must insurance cover the whole job?"
    )

    query_vector = embed_text(question, input_type="query")

    with get_engine().connect() as connection:
        matches = search_chunks(
            connection=connection,
            query_vector=query_vector,
            organisation_id="ORG-DEMO",
            policy_id="DEMO-CONTRACTOR-001",
            policy_version=1,
            document_id="PROC-CONTRACTOR-001",
            document_version=2,
            embedding_model=EMBEDDING_MODEL,
            limit=3,
        )

    if not matches:
        print("No passages found for the selected source.")
    else:
        for match in matches:
            print(
                f"{match['section_id']} | {match['title']} | "
                f"similarity={match['similarity']:.3f}"
            )
            print(match["text"])
            print()