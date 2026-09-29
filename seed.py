"""Copy the synthetic demo data from readiness.json into PostgreSQL.

Safe to run repeatedly: each run resets the demo rows to match the JSON file.
Run migrations first: `alembic upgrade head`.
"""

from sqlalchemy import text

from db import get_engine
from readiness import load_demo


def seed() -> None:
    demo = load_demo()
    policy = demo["policy"]

    # engine.begin() runs everything in one transaction:
    # either every row is written, or (on any error) none are.
    with get_engine().begin() as connection:
        connection.execute(
            text("""
                INSERT INTO policies (id, version, required_types, minimum_insurance_aud)
                VALUES (:id, :version, :required_types, :minimum_insurance_aud)
                ON CONFLICT (id, version) DO UPDATE SET
                    required_types = EXCLUDED.required_types,
                    minimum_insurance_aud = EXCLUDED.minimum_insurance_aud
            """),
            policy,
        )

        connection.execute(
            text("""
                INSERT INTO contractors (id, name, email)
                VALUES (:id, :name, :email)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email
            """),
            demo["contractors"],
        )

        connection.execute(
            text("""
                INSERT INTO jobs (id, organisation_id, status, start_date, end_date,
                                  policy_id, policy_version)
                VALUES (:id, :organisation_id, :status, :start_date, :end_date,
                        :policy_id, :policy_version)
                ON CONFLICT (id) DO UPDATE SET
                    organisation_id = EXCLUDED.organisation_id,
                    status = EXCLUDED.status,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    policy_id = EXCLUDED.policy_id,
                    policy_version = EXCLUDED.policy_version
            """),
            demo["jobs"],
        )

        job_ids = [job["id"] for job in demo["jobs"]]
        connection.execute(
            text("DELETE FROM job_contractors WHERE job_id = ANY(:job_ids)"),
            {"job_ids": job_ids},
        )
        connection.execute(
            text("INSERT INTO job_contractors (job_id, contractor_id) VALUES (:job_id, :contractor_id)"),
            [
                {"job_id": job["id"], "contractor_id": contractor_id}
                for job in demo["jobs"]
                for contractor_id in job["contractor_ids"]
            ],
        )

        connection.execute(
            text("""
                INSERT INTO documents (id, contractor_id, type, review_status,
                                       valid_from, valid_to, coverage_amount, currency)
                VALUES (:id, :contractor_id, :type, :review_status,
                        :valid_from, :valid_to, :coverage_amount, :currency)
                ON CONFLICT (id) DO UPDATE SET
                    contractor_id = EXCLUDED.contractor_id,
                    type = EXCLUDED.type,
                    review_status = EXCLUDED.review_status,
                    valid_from = EXCLUDED.valid_from,
                    valid_to = EXCLUDED.valid_to,
                    coverage_amount = EXCLUDED.coverage_amount,
                    currency = EXCLUDED.currency
            """),
            # Licences have no amount or currency; fill the gaps with None (SQL NULL).
            [
                {"coverage_amount": None, "currency": None, **document}
                for document in demo["documents"]
            ],
        )

    print(
        f"Seeded {len(demo['jobs'])} jobs, {len(demo['contractors'])} contractors, "
        f"{len(demo['documents'])} documents."
    )


if __name__ == "__main__":
    seed()
