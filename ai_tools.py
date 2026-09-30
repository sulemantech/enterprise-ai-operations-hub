
ASSESS_JOB_TOOL = {
    "name": "get_job_assessment",
    "description": (
        "Check readiness for one job using its contractor documents "
        "and policy. Returns job details, documents, policy, status, "
        "and reason. Use when asked about a specific job's readiness. "
        "If no job ID is provided, ask the user for it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "description": "The job ID supplied by the user, for example JOB-102",
            }
        },
        "required": ["job_id"],
        "additionalProperties": False,
    },
}
