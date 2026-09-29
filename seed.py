"""Reset PostgreSQL to the synthetic demo data.

Loads the four hand-written jobs from data/demo/readiness.json (the ones the
tests check) plus a larger generated dataset from demo_data.py.

    python seed.py            # fixture + generated data
    python seed.py --small    # the four fixture jobs only

Every run deletes all rows first, so it always produces the same clean state.
Run migrations first: `alembic upgrade head`.
"""

import sys
from collections import Counter

from sqlalchemy import text

import demo_data
from db import get_engine
from readiness import assess_job, load_demo


def build_dataset(include_generated: bool) -> dict:
    fixture = load_demo()
    data = {
        "policies": [fixture["policy"]],
        "contractors": fixture["contractors"],
        "jobs": fixture["jobs"],
        "documents": fixture["documents"],
    }
    if include_generated:
        generated = demo_data.generate()
        # The generated standard policy is the fixture's policy; keep one copy.
        assert fixture["policy"] in generated["policies"]
        data["policies"] = generated["policies"]
        for key in ("contractors", "jobs", "documents"):
            data[key] = data[key] + generated[key]
            ids = [record["id"] for record in data[key]]
            assert len(ids) == len(set(ids)), f"duplicate {key} id"
    return data


def seed(include_generated: bool = True) -> None:
    data = build_dataset(include_generated)

    # engine.begin() runs everything in one transaction:
    # either every row is written, or (on any error) none are.
    with get_engine().begin() as connection:
        connection.execute(text("TRUNCATE job_contractors, documents, jobs, contractors, policies"))

        connection.execute(
            text("""
                INSERT INTO policies (id, version, required_types, minimum_insurance_aud)
                VALUES (:id, :version, :required_types, :minimum_insurance_aud)
            """),
            data["policies"],
        )
        connection.execute(
            text("INSERT INTO contractors (id, name, email, trade) VALUES (:id, :name, :email, :trade)"),
            [{"trade": None, **contractor} for contractor in data["contractors"]],
        )
        connection.execute(
            text("""
                INSERT INTO jobs (id, organisation_id, status, title, site, start_date, end_date,
                                  policy_id, policy_version)
                VALUES (:id, :organisation_id, :status, :title, :site, :start_date, :end_date,
                        :policy_id, :policy_version)
            """),
            [{"title": None, "site": None, **job} for job in data["jobs"]],
        )
        connection.execute(
            text("INSERT INTO job_contractors (job_id, contractor_id) VALUES (:job_id, :contractor_id)"),
            [
                {"job_id": job["id"], "contractor_id": contractor_id}
                for job in data["jobs"]
                for contractor_id in job["contractor_ids"]
            ],
        )
        connection.execute(
            text("""
                INSERT INTO documents (id, contractor_id, type, review_status,
                                       valid_from, valid_to, coverage_amount, currency)
                VALUES (:id, :contractor_id, :type, :review_status,
                        :valid_from, :valid_to, :coverage_amount, :currency)
            """),
            # Licences have no amount or currency; fill the gaps with None (SQL NULL).
            [{"coverage_amount": None, "currency": None, **document} for document in data["documents"]],
        )

    print(
        f"Seeded {len(data['jobs'])} jobs, {len(data['contractors'])} contractors, "
        f"{len(data['documents'])} documents, {len(data['policies'])} policies."
    )
    print_summary(data)


def print_summary(data: dict) -> None:
    """Show the spread of results the rules produce for this data."""
    policies = {(p["id"], p["version"]): p for p in data["policies"]}
    results = Counter(
        assess_job(job, data["documents"], policies[(job["policy_id"], job["policy_version"])])
        for job in data["jobs"]
    )
    for (status, reason), count in sorted(results.items(), key=lambda item: -item[1]):
        print(f"  {count:4}  {status:<13} {reason}")


if __name__ == "__main__":
    seed(include_generated="--small" not in sys.argv)
