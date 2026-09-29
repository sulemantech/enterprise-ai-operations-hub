"""Generate a larger, realistic synthetic dataset for demonstrations.

Deterministic: the same seed always produces the same records, so demos and
screenshots are repeatable. Every name, email and site is invented; emails use
the reserved .invalid domain so nothing can ever be delivered.

Each contractor gets a compliance *profile* describing a real-world situation.
The profiles only shape the documents - the readiness result of every job is
still decided by readiness.py.
"""

import random
from datetime import date, timedelta

SEED = 20261001
FIRST_JOB_DAY = date(2026, 9, 28)
LAST_JOB_DAY = date(2026, 11, 27)
JOB_COUNT = 140

STANDARD_POLICY = {
    "id": "DEMO-CONTRACTOR-001",
    "version": 1,
    "required_types": ["insurance", "trade_licence"],
    "minimum_insurance_aud": 5_000_000,
}
HIGH_RISK_POLICY = {
    "id": "DEMO-HIGH-RISK-001",
    "version": 1,
    "required_types": ["insurance", "trade_licence", "safety_induction"],
    "minimum_insurance_aud": 20_000_000,
}

TRADES = {
    "Electrical": ["Switchboard upgrade", "LED lighting retrofit", "Test and tag", "EV charger installation",
                   "Emergency lighting service", "Data cabling"],
    "Plumbing": ["Hot water system replacement", "Backflow prevention test", "Bathroom rough-in",
                 "Blocked drain repair", "Gas fitting"],
    "HVAC": ["Split system installation", "Chiller maintenance", "Ductwork cleaning", "Cooling tower service"],
    "Carpentry": ["Office fit-out partitions", "Door hardware replacement", "Deck repair", "Joinery installation"],
    "Painting": ["Stairwell repaint", "Exterior facade painting", "Line marking", "Anti-graffiti coating"],
    "Roofing": ["Roof leak repair", "Gutter replacement", "Skylight installation", "Roof safety anchor install"],
    "Scaffolding": ["Scaffold erection", "Scaffold inspection", "Edge protection install"],
    "Fire Services": ["Sprinkler inspection", "Fire alarm service", "Hydrant flow test", "Fire door certification"],
}
HIGH_RISK_TRADES = {"Roofing", "Scaffolding", "Fire Services"}

NAME_WORDS = ["Harbour", "Summit", "Blue Gum", "Ironbark", "Coastal", "Southern Cross", "Redgum", "Bridgeview",
              "Northside", "Westfield", "Greenway", "Kingsford", "Riverstone", "Parkside", "Eastgate",
              "Silver Wattle", "Highline", "Clearwater", "Bluestone", "Sandstone", "Waratah", "Orchard",
              "Headland", "Lakeside", "Cedar", "Beacon", "Granite", "Meridian", "Horizon", "Pinnacle",
              "Anchor", "Ember"]
SITES = ["Parramatta", "North Sydney", "Chatswood", "Penrith", "Liverpool", "Bondi Junction", "Macquarie Park",
         "Hornsby", "Blacktown", "Hurstville", "Newtown", "Manly", "Castle Hill", "Campbelltown", "Burwood",
         "Mascot", "Rhodes", "Ultimo", "Surry Hills", "Olympic Park"]

# How many contractors get each situation. The mix is chosen so a demo shows
# every result type, with most work ready - as in a healthy real business.
PROFILES = (
    ["compliant"] * 14
    + ["insurance_expires"] * 3   # expires mid-period: early jobs ready, later ones blocked
    + ["insurance_renewed"] * 2   # old policy expires, a verified renewal takes over
    + ["renewal_pending"] * 2     # renewal uploaded but not yet reviewed
    + ["missing_licence"] * 2
    + ["licence_pending"] * 2
    + ["low_coverage"] * 2
    + ["licence_starts_late"] * 1  # new licence only valid from mid-October
    + ["missing_induction"] * 2    # only matters for high-risk jobs
)


def _date_between(rng: random.Random, first: date, last: date) -> date:
    return first + timedelta(days=rng.randint(0, (last - first).days))


def _documents_for(rng: random.Random, contractor: dict, profile: str, next_id) -> list[dict]:
    def document(type_, valid_from, valid_to, review_status="verified", coverage=None):
        record = {
            "id": next_id(),
            "contractor_id": contractor["id"],
            "type": type_,
            "review_status": review_status,
            "valid_from": valid_from.isoformat(),
            "valid_to": valid_to.isoformat(),
            "coverage_amount": None,
            "currency": None,
        }
        if type_ == "insurance":
            record["coverage_amount"] = coverage
            record["currency"] = "AUD"
        return record

    high_risk = contractor["trade"] in HIGH_RISK_TRADES
    coverage = rng.choice([20_000_000, 20_000_000, 30_000_000] if high_risk else [5_000_000, 10_000_000, 20_000_000])
    year_start = date(2026, 1, 1) + timedelta(days=rng.randint(0, 150))
    documents = []

    # Insurance
    if profile == "insurance_expires":
        documents.append(document("insurance", year_start, _date_between(rng, date(2026, 10, 12), date(2026, 11, 13)),
                                  coverage=coverage))
    elif profile in ("insurance_renewed", "renewal_pending"):
        switch = _date_between(rng, date(2026, 10, 15), date(2026, 11, 5))
        documents.append(document("insurance", year_start, switch - timedelta(days=1), coverage=coverage))
        status = "verified" if profile == "insurance_renewed" else "pending"
        documents.append(document("insurance", switch, switch + timedelta(days=364), status, coverage))
    elif profile == "low_coverage":
        documents.append(document("insurance", year_start, year_start + timedelta(days=364),
                                  coverage=rng.choice([2_000_000, 3_000_000])))
    else:
        documents.append(document("insurance", year_start, year_start + timedelta(days=364), coverage=coverage))

    # Trade licence
    licence_start = date(2025, rng.randint(1, 12), 1)
    if profile == "licence_pending":
        documents.append(document("trade_licence", licence_start, licence_start + timedelta(days=3 * 365), "pending"))
    elif profile == "licence_starts_late":
        documents.append(document("trade_licence", date(2026, 10, 16), date(2029, 10, 15)))
    elif profile != "missing_licence":
        documents.append(document("trade_licence", licence_start, licence_start + timedelta(days=3 * 365)))

    # Safety induction (only trades that do high-risk work hold one)
    if high_risk and profile != "missing_induction":
        start = date(2026, rng.randint(1, 8), 1)
        documents.append(document("safety_induction", start, start + timedelta(days=2 * 365)))

    return documents


def generate() -> dict:
    """Return contractors, jobs, documents and policies in the readiness.json shape."""
    rng = random.Random(SEED)

    trades = list(TRADES)
    profiles = PROFILES[:]
    rng.shuffle(profiles)
    names = rng.sample(NAME_WORDS, len(profiles))

    contractors = []
    for number, (profile, word) in enumerate(zip(profiles, names), start=101):
        trade = trades[number % len(trades)]
        # A missing induction only shows up for trades that need one.
        if profile == "missing_induction":
            trade = rng.choice(sorted(HIGH_RISK_TRADES))
        contractors.append({
            "id": f"CON-{number}",
            "name": f"{word} {trade}",
            "email": f"{word.lower().replace(' ', '')}.{trade.lower().replace(' ', '')}@example.invalid",
            "trade": trade,
            "profile": profile,
        })

    document_ids = iter(range(1001, 10_000))
    documents = []
    for contractor in contractors:
        documents += _documents_for(rng, contractor, contractor["profile"], lambda: f"DOC-{next(document_ids)}")

    jobs = []
    for number in range(1001, 1001 + JOB_COUNT):
        contractor = rng.choice(contractors)
        contractor_ids = [contractor["id"]]
        # Some jobs need a second contractor, e.g. an electrician alongside HVAC.
        if rng.random() < 0.15:
            contractor_ids.append(rng.choice([c for c in contractors if c is not contractor])["id"])

        start = _date_between(rng, FIRST_JOB_DAY, LAST_JOB_DAY)
        high_risk = contractor["trade"] in HIGH_RISK_TRADES and rng.random() < 0.7
        policy = HIGH_RISK_POLICY if high_risk else STANDARD_POLICY
        jobs.append({
            "id": f"JOB-{number}",
            "organisation_id": "ORG-DEMO",
            "status": "scheduled",
            "title": rng.choice(TRADES[contractor["trade"]]),
            "site": rng.choice(SITES),
            "contractor_ids": contractor_ids,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=rng.choice([0, 0, 0, 1, 1, 2, 4]))).isoformat(),
            "policy_id": policy["id"],
            "policy_version": policy["version"],
        })

    for contractor in contractors:
        del contractor["profile"]  # Describes how data was generated; not a stored fact.

    return {
        "policies": [STANDARD_POLICY, HIGH_RISK_POLICY],
        "contractors": contractors,
        "jobs": jobs,
        "documents": documents,
    }
