import repository
from db import get_engine
from readiness import assess_job

def get_job_assessment(job_id:str) -> dict:
    with get_engine().connect() as conn:
        job = repository.get_job(conn, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")
        
        documents = repository.documents_for(
            connection=conn,
            contractor_ids=job["contractor_ids"],
        )
        policy = repository.get_policy(conn, job["policy_id"], job["policy_version"])

        status, reason = assess_job(job, documents, policy)
        
        return {
            "job":job,
            "documents": documents,
            "policy": policy,
            "status": status,
            "reason": reason,
        }
    