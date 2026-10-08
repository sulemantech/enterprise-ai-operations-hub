
from multiprocessing import connection

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Connection, bindparam, text


def save_chunk(connection: Connection, chunk: dict) -> int:
    """Insert or update a chunk and return its ID; the caller owns the transaction."""
    result = connection.execute(
        text("""
            INSERT INTO knowledge_chunks (
                organisation_id, policy_id, policy_version,
                document_id, document_version, section_id,
                title, text, implementation_scope,
                content_hash, embedding_model, embedding,
                source_path, source_status, synthetic
            ) VALUES (
                :organisation_id, :policy_id, :policy_version,
                :document_id, :document_version, :section_id,
                :title, :text, :implementation_scope,
                :content_hash, :embedding_model, :embedding,
                :source_path, :source_status, :synthetic
            )
            ON CONFLICT ON CONSTRAINT uq_knowledge_chunk_source_model
            DO UPDATE SET
                title = EXCLUDED.title,
                text = EXCLUDED.text,
                source_path = EXCLUDED.source_path,
                source_status = EXCLUDED.source_status,
                synthetic = EXCLUDED.synthetic,
                implementation_scope = EXCLUDED.implementation_scope,
                content_hash = EXCLUDED.content_hash,
                embedding = EXCLUDED.embedding
            RETURNING id
        """).bindparams(
            bindparam("embedding", type_=VECTOR(1024))
        ),
        chunk,
    )
    return result.scalar_one()


def list_chunk_summaries(
    connection: Connection,
    organisation_id: str,
    policy_id: str,
    policy_version: int,
    document_id: str,
    document_version: int,
    embedding_model: str,
) -> list[dict]:
    rows = connection.execute(
        text("""
            SELECT section_id, title, content_hash,
                   vector_dims(embedding) AS dimensions
            FROM knowledge_chunks
            WHERE organisation_id = :organisation_id
              AND policy_id = :policy_id
              AND policy_version = :policy_version
              AND document_id = :document_id
              AND document_version = :document_version
              AND embedding_model = :embedding_model
            ORDER BY section_id
        """),
        {
            "organisation_id": organisation_id,
            "policy_id": policy_id,
            "policy_version": policy_version,
            "document_id": document_id,
            "document_version": document_version,
            "embedding_model": embedding_model,
        },
    )

    return [dict(row) for row in rows.mappings()]

def search_chunks(
    connection: Connection,
    query_vector: list[float],
    organisation_id: str,
    policy_id: str,
    policy_version: int,
    document_id: str,
    document_version: int,
    embedding_model: str,
    limit: int = 3,
) -> list[dict]:
    if not 1 <= limit <= 12:
        raise ValueError("limit must be between 1 and 12")
    rows = connection.execute(
        text("""
                SELECT section_id, title, text,
                   organisation_id, policy_id, policy_version,
                   document_id, document_version, source_path,
                   source_status, synthetic, implementation_scope,
                   vector_dims(embedding) AS dimensions,
                   1 - (embedding <=> :query_vector) AS similarity
            FROM knowledge_chunks
            WHERE organisation_id = :organisation_id
              AND policy_id = :policy_id
              AND policy_version = :policy_version
              AND document_id = :document_id
              AND document_version = :document_version
              AND embedding_model = :embedding_model
            ORDER BY embedding <=> :query_vector
            LIMIT :limit
        """).bindparams(
            bindparam("query_vector", type_=VECTOR(1024))
        ),
        {
            "query_vector": query_vector,
            "organisation_id": organisation_id,
            "policy_id": policy_id,
            "policy_version": policy_version,
            "document_id": document_id,
            "document_version": document_version,
            "embedding_model": embedding_model,
            "limit": limit,
        },
    )

    return [dict(row) for row in rows.mappings()]
