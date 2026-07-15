# MatVerse Claims and Maturity Policy

**Version:** 1.0.0  
**Effective date:** 2026-07-15  
**Default posture:** fail closed

## 1. Purpose

This policy prevents descriptions, generated reports and local demonstrations from being promoted into factual claims about scientific validity, production readiness, institutional closure, security, performance or technology readiness.

## 2. Evidence classes

Every material statement must be classified as exactly one of:

- `OBSERVED`: directly read or measured from a retained artifact.
- `REPRODUCED`: independently rerun from declared inputs and environment.
- `INFERRED`: reasoned from observations, with assumptions stated.
- `HYPOTHESIS`: plausible but not yet tested.
- `DECLARED`: stated by an author or system but not independently verified.
- `REFUTED`: contradicted by stronger evidence.

Unclassified statements are treated as `DECLARED`.

## 3. Restricted claims

The following labels are prohibited without a linked evidence pack:

- `production`, `production-ready`, `deployed`;
- `validated`, `scientifically proven`, `externally verified`;
- `institutionally closed`, `irreversible`, `sovereign` as an achieved state;
- any TRL level;
- throughput, latency, accuracy, false-positive rate, cost or reliability numbers;
- security, privacy, post-quantum or compliance guarantees;
- blockchain transaction, DOI, release, customer, revenue or adoption claims.

## 4. Evidence pack minimum

A restricted claim requires:

```yaml
claim_id: stable identifier
claim_text: exact statement
scope: what the statement covers and excludes
evidence_class: OBSERVED or REPRODUCED
source_commit: immutable commit SHA
environment: OS, runtime and dependency lock
inputs: hashes and provenance
commands: exact executable commands
outputs: retained logs and artifacts
expected_result: machine-checkable condition
actual_result: observed condition
replay: second execution result
reviewer: independent human or environment
limitations: known failure modes and uncertainty
```

Missing fields force `HOLD`.

## 5. Synthetic and mock data

Mock, synthetic, generated or manually chosen inputs must be labeled in filenames, reports and user interfaces. They may prove code-path behavior, but they cannot establish external performance, scientific validity, institutional closure or production maturity.

Allowed wording:

> Demonstrated locally with synthetic inputs; external validity not established.

Blocked wording:

> Validated institutionally, TRL 7, production proven.

## 6. Historical correction rule

The commit `5f82e8881bd4c40175f8f4b87594b05d225360b0` in `matverse-acoa/matverse` contains a report titled as institutional closure at TRL 7 while the included generator identifies its input as a mock dataset and writes to an environment-specific absolute path.

Until a complete evidence pack is produced, the following historical statements are reclassified:

```text
TRL 7: HOLD_UNVERIFIED
INSTITUTIONALLY_CLOSED: HOLD_UNVERIFIED
external reproducibility: NOT_ESTABLISHED
local deterministic demonstration: PARTIAL
```

This policy does not delete the historical commit. It records the epistemic correction and requires future surfaces to display the corrected state.

## 7. Claim lifecycle

```text
HYPOTHESIS
-> TEST_PLAN
-> OBSERVED
-> REPRODUCED
-> EXTERNALLY_VALIDATED
-> MAINTAINED_CLAIM
```

A claim regresses automatically when its dependencies, environment, dataset or implementation change materially.

## 8. Enforcement

Pull requests that introduce restricted claims must link their evidence pack. CI should reject unqualified restricted terms in release metadata and public-facing documentation unless the same change includes the required evidence manifest.

The final gate is one of:

- `PASS`: claim and evidence match.
- `HOLD`: evidence incomplete or stale.
- `BLOCK`: claim materially exceeds evidence.
- `ESCALATE`: integrity, provenance or conflict-of-interest concern.
