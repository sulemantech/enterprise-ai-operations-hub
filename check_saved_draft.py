from db import get_engine
from followup_repository import get_draft

with get_engine().connect() as connection:
    draft = get_draft(connection, 1, "ORG-DEMO")

assert draft is not None
assert draft["status"] == "draft"
assert draft["job_id"] == "JOB-102"
assert draft["recipient"] == "two@example.invalid"
assert draft["evidence_ids"] == ["DOC-003"]
assert draft["source_snapshot"]["assessment"]["reason"] == (
    "EXPIRES_BEFORE_JOB_END"
)
assert "2026-10-09" in draft["body"]

print("Saved draft read-back checks passed.")
print("Created at:", draft["created_at"])