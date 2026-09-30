# Contractor Approval and Monitoring Procedure

Synthetic demo procedure — not an official FocusIMS or FocusBIS document.

- Organisation: Demo Field Services (`ORG-DEMO`)
- Document ID: `PROC-CONTRACTOR-001`; document version: 2 (draft)
- Policy ID: `DEMO-CONTRACTOR-001`; policy version: 1
- Scope: contractor onboarding and job review for fictional electrical maintenance work in NSW; automated checks cover only insurance and trade-licence metadata
- Source status: demo baseline, not client-approved or validated against an ISO standard

## How to use this procedure

Demo Field Services engages electrical subcontractors for maintenance at commercial premises. The coordinator collects evidence, the operations manager checks job requirements, and the site supervisor confirms local arrangements before work starts. These are fictional company responsibilities for the demonstration.

CP-01 to CP-06 describe the existing automated document checks. CP-07 to CP-12 describe proposed human processes; their completion is not recorded or verified by the current application. The assistant may explain these processes but must report their job-specific completion as unknown unless suitable records become available.

Document version 2 adds practical workflow detail; structured policy version 1 and its automated thresholds remain unchanged. This is a draft for learning, not a procedure approved for use on a real site.

## CP-01 — Purpose and assignment

The job must have at least one assigned contractor. No assignment produces BLOCKED / NO_CONTRACTOR. This procedure supports contractor document review and evidence preparation for the fictional organisation.

## CP-02 — Required evidence

Each assigned contractor requires insurance and a trade licence. An absent required document type produces BLOCKED / MISSING_DOCUMENT. At least one document per type must independently meet applicable date, coverage and review checks. The demo does not combine multiple documents to establish continuous coverage.

## CP-03 — Validity throughout the job

Evidence must be valid from no later than the job start and remain valid through the job end. Both boundaries are inclusive. Evidence ending before the job ends fails with EXPIRES_BEFORE_JOB_END. If the end covers the job but validity starts after the job start, it fails with NOT_VALID_AT_JOB_START. Either is BLOCKED when no qualifying alternative satisfies that requirement.

## CP-04 — Insurance amount

DEMO-CONTRACTOR-001 version 1 requires at least AUD 5,000,000 insurance coverage. Exactly that amount meets the amount check. A known lower amount, including zero, fails with BLOCKED / INSUFFICIENT_COVERAGE. An unknown amount yields NEEDS_REVIEW / UNKNOWN_COVERAGE when date checks pass. The demo assumes AUD and performs no currency conversion. This is a fictional company threshold, not an ISO or legal requirement. Other policy IDs may have different thresholds.

## CP-05 — Reviewed evidence

Evidence must have recorded review status `verified`. If dates and amount pass but review status does not, return NEEDS_REVIEW / UNVERIFIED_DOCUMENT. A designated coordinator reviews evidence before its status is updated. The demo reads review metadata; AI does not authenticate documents or independently establish competence.

## CP-06 — Meaning of the assessment

READY / REQUIREMENTS_MET means these configured document checks pass for the assigned contractors. It is not a certification decision, a complete safety assessment or permission to commence work.

The implementation returns one overall status/reason. It checks dates, then amount, then review status. A qualifying alternative satisfies the required type. If every candidate fails, a reviewable candidate takes precedence over blocked candidates for that type; across unmet requirements, BLOCKED takes precedence over NEEDS_REVIEW. A single returned reason does not mean there are no other issues.

## CP-07 — Follow-up and reassessment

Planned workflow: prepare a replacement-evidence request for manager review, or ask a coordinator to review evidence that only needs verification. Show the exact recipient and message before approval. Send approved demo messages to the capture inbox and record their outcome separately from readiness.

Sending a message does not resolve the gap. Update reviewed operational records and reassess. Approval, delivery history and audit exports are not yet implemented; the assistant must not claim they occurred without stored evidence.

## CP-08 — Responsibilities and onboarding

Proposed manual process:

| Responsible person | Action | Record to keep |
| --- | --- | --- |
| Operations manager | Define work scope, site, dates and applicable client requirements before requesting evidence | Job brief and requirement checklist |
| Contractor representative | Provide business identity, nominated contact and documents relevant to the work | Contractor submission with received date |
| Coordinator | Check document readability, named entity, dates and recorded details; refer inconsistencies for review | Document reference, reviewer, review date and notes |
| Safety reviewer | Assess task-specific safety documentation and unresolved suitability questions | Review outcome and required actions |
| Site supervisor | Confirm induction and agreed site arrangements before authorising work under the company's site process | Site checklist and supervisor decision |

A business registration or insurance certificate alone does not establish suitability for the job. Request additional evidence based on actual work and site requirements. Current database records do not contain a complete onboarding or reviewer-history record.

## CP-09 — Evidence review checklist

Proposed manual process before recording evidence as verified:

1. Match the document holder to the contractor or named worker, as applicable. Resolve differences rather than assuming related entities are interchangeable.
2. Confirm document type, issuer, reference number and legibility. Check relevant licence scope, restrictions and current standing through an appropriate authoritative source where applicable.
3. Compare validity dates with the whole assigned job period. A promise to renew is not replacement evidence.
4. For insurance, confirm the policy type, insured entity, relevant activities, amount and currency; refer exclusions or ambiguous coverage to a qualified reviewer. The current generic `insurance` record cannot make these checks.
5. Determine whether other insurance, worker competencies or client-specific evidence is needed for this engagement. Record applicability and the review basis; do not assume every contractor requires the same additional documents.
6. Record acceptance, clarification needed or rejection, with reviewer and reasons. Do not label an uploaded document verified solely because a file exists.

The current application checks stored dates, amount and `review_status` only. It does not query licence registers or read policy wording. These additional reviews must not be inferred from READY.

## CP-10 — Task and site safety review

Proposed manual process: identify the actual task, work location, affected people and interaction with other contractors or occupants. Agree responsibilities, communication, access and emergency arrangements with the relevant parties. This approach is informed by [Safe Work Australia guidance on consultation, cooperation and coordination](https://www.safeworkaustralia.gov.au/safety-topic/managing-health-and-safety/consultation/consulting-cooperating-and-coordinating-activities-other-duty-holders).

Have a competent reviewer determine whether the task is high risk construction work. Where a safe work method statement (SWMS) is required, review its relevance to the specific site, hazards and controls. A generic uploaded SWMS is not proof that controls have been implemented. SafeWork NSW explains the high risk construction work trigger and site-specific review requirements in its [SWMS guidance](https://www.safework.nsw.gov.au/your-industry/construction/construction/general-requirements/prepare-safe-work-method-statement).

Record applicable induction, competency and permit requirements, and check their completion through the site process. Do not infer a SWMS requirement solely from a job title such as “lighting retrofit.” The assistant has no task-risk, induction, SWMS or permit records today and must not claim these checks passed.

## CP-11 — Unresolved items and changes

Proposed company workflow: review evidence while scheduling and recheck it before the planned start. A blocked or unresolved document finding is referred to the operations manager for rescheduling, replacement evidence or further investigation. Sending a request or receiving verbal assurance does not clear a finding. The prototype has no override function.

For each follow-up, record the job, contractor, specific missing or disputed evidence, owner and agreed response date. The response date is set for the job; this procedure does not invent a universal statutory deadline.

Reassess when job dates, contractor assignment, submitted evidence or applicable requirements change. Refer changes in work scope or site conditions to the safety reviewer and site supervisor. Keep approval to send a message separate from a decision permitting work.

## CP-12 — Review record and worked example

Proposed review record: job and contractor IDs; procedure and policy versions; document references; reviewer and date; outstanding items; assigned actions; and the evidence supporting closure. Retain superseded versions according to an approved organisational retention schedule; no universal retention period is asserted here. The prototype does not yet implement this complete record or an audit export.

For JOB-102, the office lighting retrofit runs 6–9 October 2026. DOC-003 ends on 7 October, so it does not cover the full job under CP-03. The coordinator should request insurance evidence covering the assigned period and review it before reassessment. The manager must resolve the document issue through the scheduling process. No completed follow-up or site authorisation can be inferred from the existing records.

This example supports separate answers to “Why is it blocked?”, “Who should act?” and “What evidence would resolve the gap?” It cannot establish whether induction or task-specific safety arrangements are complete.

## Reference basis and revision history

The linked public Australian guidance informed CP-10. The roles, insurance threshold and workflow choices elsewhere are fictional company design choices. This document is not a legal checklist, a reproduction of an ISO standard or a claim of ISO conformity. No private FocusIMS/FocusBIS materials were used.

| Document version | Change | Structured policy |
| --- | --- | --- |
| 1 | Initial synthetic document rules and planned follow-up | DEMO-CONTRACTOR-001 v1 |
| 2 draft | Added responsibilities, practical review, site coordination, change handling and review records | DEMO-CONTRACTOR-001 v1 unchanged |
