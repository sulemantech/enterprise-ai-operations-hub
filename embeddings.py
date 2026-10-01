import voyageai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

EMBEDDING_MODEL = "voyage-4-lite"
EMBEDDING_DIMENSION = 1024

def embed_text(text: str, input_type: str = "document") -> list[float]:
    """Return the embedding vector for the given text."""
    if not text.strip():
        raise ValueError("Text must not be empty")
    if input_type not in ("document", "query"):
        raise ValueError("input_type must be 'document' or 'query'")
    client = voyageai.Client()

    response = client.embed(
        texts=[text],
        model=EMBEDDING_MODEL,
        input_type=input_type,
        output_dimension=EMBEDDING_DIMENSION,
        truncation=False,
    )
    vector = response.embeddings[0]

    if len(vector) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, got {len(vector)}"
        )

    return vector