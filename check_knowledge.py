from db import get_engine
from embeddings import EMBEDDING_MODEL, EMBEDDING_DIMENSION
from knowledge_repository import list_chunk_summaries


if __name__ == "__main__":
    with get_engine().connect() as connection:
        rows = list_chunk_summaries(
            connection=connection,
            organisation_id="ORG-DEMO",
            policy_id="DEMO-CONTRACTOR-001",
            policy_version=1,
            document_id="PROC-CONTRACTOR-001",
            document_version=2,
            embedding_model=EMBEDDING_MODEL,
        )

    expected_ids = {f"CP-{number:02d}" for number in range(1, 13)}
    print("Stored sections:", [row["section_id"] for row in rows])
    assert len(rows) == 12, f"Expected 12 rows, found {len(rows)}"
    assert {row["section_id"] for row in rows} == expected_ids

    for row in rows:
        assert row["dimensions"] == EMBEDDING_DIMENSION
        print(row["section_id"], row["title"], row["dimensions"])

    print("Stored knowledge checks passed.")