import json
import time
from pathlib import Path
from embeddings import embed_text, EMBEDDING_MODEL
import hashlib
from db import get_engine
from knowledge_repository import save_chunk

def load_procedure(str_path:Path) -> str:
    with str_path.open(encoding="utf-8") as file:
        return file.read()

def split_sections(text: str) -> list[dict]:
    sections = []
    current_section = None

    for line in text.splitlines():
        if line.startswith("## "):
            # Save the previous section before processing the new heading.
            if current_section is not None:
                current_section["text"] = "\n".join(current_section["text"]).strip()
                sections.append(current_section)

            # Only CP sections become active sections.
            if line.startswith("## CP-"):
                heading = line[3:]
                section_id, title = heading.split(" — ", 1)

                current_section = {
                    "section_id": section_id,
                    "title": title,
                    "text": [],
                }
            else:
                current_section = None

        elif current_section is not None:
            current_section["text"].append(line)

    # Save the final section.
    if current_section is not None:
        current_section["text"] = "\n".join(current_section["text"]).strip()
        sections.append(current_section)

    return sections

def validate_sections(sections: list[dict]) -> None:
    """Raise ValueError if any section is missing required fields."""
    if not sections:
        raise ValueError("No sections found in the procedure text.")
    seen_ids = set()
    for section in sections:
        if not section.get("section_id"):
            raise ValueError(f"Section missing section_id: {section}")
        
        section_id = section["section_id"]

        if section_id in seen_ids:
            raise ValueError(f"Section ID duplicated: {section_id}")
        seen_ids.add(section_id)

        if not section.get("title") or not section["title"].strip():
            raise ValueError(f"Section missing title: {section}")
        if not section.get("text") or not section["text"].strip():
            raise ValueError(f"Section missing text: {section}")


def build_chunks(sections: list[dict], metadata: dict) -> list[dict]:
    """Attach source metadata and implementation scope to each complete section."""
    chunks = []
    validate_sections(sections)

    for section in sections:
        text = section["text"]
        section_number = int(section["section_id"].split("-")[1])
        if 1 <=section_number<=6:
            implementation_scope = "implemented_checks"
        elif 7 <= section_number <= 12:
            implementation_scope = "proposed_manual_process"
        else:
            raise ValueError(f"Unexpected section number: {section_number}")
        chunks.append({
            **metadata,
            "section_id": section["section_id"],
            "title": section["title"],
            "text": text,
            "implementation_scope": implementation_scope,
            "content_hash": calculate_content_hash(
                section["title"], section["text"]
            ),
        })
    return chunks

def calculate_content_hash(title: str, text: str) -> str:
    """Return a SHA256 hash of the title and text."""
    content = f"{title}\n\n{text}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def embed_chunk(chunk: dict) -> dict:
    """Return a new chunk dictionary with its embedding model and vector."""
    embedding_text = f"{chunk['title']}\n\n{chunk['text']}"
    embedded_text = embed_text(embedding_text, input_type="document")
    return {
        **chunk,
        "embedding_model": EMBEDDING_MODEL,
        "embedding": embedded_text,
    }

if __name__ == "__main__":
    procedure_path = Path(__file__).parent / "docs" / "knowledge" / "contractor_approval_procedure.md"
    procedure_text = load_procedure(procedure_path)
    sections = split_sections(procedure_text)
    metadata = {
        "organisation_id": "ORG-DEMO",
        "policy_id": "DEMO-CONTRACTOR-001",
        "policy_version": 1,
        "document_id": "PROC-CONTRACTOR-001",
        "document_version": 2,
        "source_path": procedure_path.relative_to(Path(__file__).parent).as_posix(),
        "source_status": "draft",
        "synthetic": True,
    }
    chunks = build_chunks(sections, metadata)
    expected_ids = {f"CP-{number:02d}" for number in range(1, 13)}
    actual_ids = {chunk["section_id"] for chunk in chunks}

    assert actual_ids == expected_ids, "Missing or unexpected CP sections"
    assert len(chunks) == 12, "Expected exactly 12 chunks"

    cp03 = next(chunk for chunk in chunks if chunk["section_id"] == "CP-03")
    assert cp03["policy_version"] == 1
    assert cp03["document_version"] == 2
    assert cp03["implementation_scope"] == "implemented_checks"

    cp12 = next(chunk for chunk in chunks if chunk["section_id"] == "CP-12")
    assert "## Reference basis and revision history" not in cp12["text"]

    print("Chunk checks passed.")

    for chunk in chunks:
        print(f"Section {chunk['section_id']}: {chunk['title']} ({chunk['implementation_scope']})")
    print(json.dumps(chunks[2], indent=2, ensure_ascii=False))

    saved_count = 0

    for chunk in chunks:
        embedded_chunk = embed_chunk(chunk)

        with get_engine().begin() as connection:
            chunk_id = save_chunk(connection, embedded_chunk)

        saved_count += 1
        print(f"Saved {chunk['section_id']} with ID {chunk_id}")
        time.sleep(25)
    print(f"Finished: saved {saved_count} chunks.")

    