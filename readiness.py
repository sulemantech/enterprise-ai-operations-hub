"""First learning step: check insurance dates for one fictional job."""

import json
from datetime import date
from pathlib import Path


def insurance_covers_job(
    job_start: date,
    job_end: date,
    insurance_start: date,
    insurance_end: date,
) -> bool:
    """Return whether insurance dates cover the entire job, inclusively.

    Inputs must be valid, ordered date ranges. This checks dates only;
    document review status, coverage amounts, and licences come later.
    """
    return insurance_start <= job_start and insurance_end >= job_end

def find_insurance_documents(
        documents:list[dict], 
        contractor_id: str
        ) ->list[dict]:
    
    documents = [document for document in documents if document["contractor_id"]==contractor_id and document["type"].lower()=="insurance"]
    return documents

def assess_job(job:dict,documents:list[dict]) ->tuple[str, str]:
    matching_documents = [
        document 
        for document in documents 
        if document["contractor_id"] in job["contractor_ids"]

    ]
    for document in matching_documents:
        if date.fromisoformat(document["valid_to"]) < date.fromisoformat(job["end_date"]):
            return "BLOCKED", "EXPIRES_BEFORE_JOB_END"
    return "READY", "REQUIREMENTS_MET"

if __name__ == "__main__":
    data_path = Path(__file__).parent / "data" / "demo" / "readiness.json"
    with data_path.open(encoding="utf-8") as file:
        demo = json.load(file)
       
    job = next(job for job in demo["jobs"] if job["id"] == "JOB-102")
    # insurance = next(doc for doc in demo["documents"] if doc["id"] == "DOC-003")

    insurance_documents = find_insurance_documents(
        demo["documents"],
        job["contractor_ids"][0],
    )
    if not insurance_documents:
        print("No insurance documents found")
    else:
        for document in insurance_documents:
            covered = insurance_covers_job(
                job_start=date.fromisoformat(job["start_date"]),
                job_end=date.fromisoformat(job["end_date"]),
                insurance_start=date.fromisoformat(document["valid_from"]),
                insurance_end=date.fromisoformat(document["valid_to"]),
            )
            print(document["id"], covered)


    status, reason = assess_job(job, insurance_documents)
    print(job["id"], status, reason)

    # covered = insurance_covers_job(
    #     job_start=date.fromisoformat(job["start_date"]),
    #     job_end=date.fromisoformat(job["end_date"]),
    #     insurance_start=date.fromisoformat(insurance["valid_from"]),
    #     insurance_end=date.fromisoformat(insurance["valid_to"]),
    # )

    # print(f"Job: {job['id']} ({job['start_date']} to {job['end_date']})")
    # print(f"Insurance: {insurance['valid_from']} to {insurance['valid_to']}")
    # print(f"Insurance dates cover the whole job: {covered}")
    # if not covered:
    #     print("This job fails the insurance date check.")
