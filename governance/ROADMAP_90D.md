# MatVerse 90-Day Consolidation Roadmap

**Window:** 2026-07-15 to 2026-10-13  
**Objective:** replace portfolio expansion with one integrated, reproducible and externally replayed organism path.

## Success condition

The program succeeds only when a clean environment can execute:

```text
request
-> Cassandra evaluation
-> critical-lens report
-> Gate decision
-> authorized or blocked runtime action
-> append-only record
-> deterministic replay
-> evidence pack
```

Documentation alone does not satisfy the success condition.

## Phase 0 — Control and correction

**Window:** 2026-07-15 to 2026-07-24

Deliverables:

- merge an approved operational control charter;
- activate the claims policy and mark unsupported historical claims as `HOLD`;
- establish the portfolio registry and repository classifications;
- freeze new top-level architecture and repository creation;
- triage every open pull request as `MERGE_CANDIDATE`, `CHANGES_REQUIRED`, `HOLD` or `CLOSE`;
- reconcile the live repository count instead of relying on static expected counts.

Exit gate:

```text
CONTROL_CHARTER: PASS
CLAIMS_POLICY: PASS
PORTFOLIO_REGISTRY: PASS
OPEN_PR_TRIAGE: PASS
UNSUPPORTED_PUBLIC_CLAIMS: HOLD_OR_CORRECTED
```

## Phase 1 — Canonical contracts

**Window:** 2026-07-25 to 2026-08-13

Deliverables:

- freeze versioned schemas for intent, policy report, gate decision, action receipt and replay report;
- define interface ownership between `core`, `Cassandra`, `Gate`, `Organismo` and the evidence store;
- remove absolute paths and undeclared environment dependencies from canonical execution;
- add dependency locks and a one-command local bootstrap;
- add fail-closed validation at every boundary.

Required artifacts:

```text
schemas/intent.schema.json
schemas/policy-report.schema.json
schemas/gate-decision.schema.json
schemas/action-receipt.schema.json
schemas/replay-report.schema.json
```

Exit gate:

```text
SCHEMAS_VERSIONED: PASS
INTERFACES_UNAMBIGUOUS: PASS
ABSOLUTE_PATHS_REMOVED: PASS
BOOTSTRAP_CLEAN_ENV: PASS
```

## Phase 2 — Golden-path implementation

**Window:** 2026-08-14 to 2026-09-12

Deliverables:

- one API or CLI request enters the canonical pipeline;
- Cassandra emits a structured policy report;
- Gate produces `PASS`, `HOLD`, `BLOCK` or `ESCALATE`;
- Organismo executes only authorized adapters;
- every transition writes a hash-linked event;
- replay recomputes the terminal state from retained inputs;
- negative and adversarial cases are included.

Minimum tests:

1. valid low-risk request passes and executes;
2. missing evidence holds;
3. forbidden action blocks;
4. malformed input fails closed;
5. tampered ledger fails replay;
6. repeated clean replay produces the same terminal state;
7. human override is recorded without deleting the original decision.

Exit gate:

```text
END_TO_END_EXECUTION: PASS
NEGATIVE_CASES: PASS
TAMPER_DETECTION: PASS
DETERMINISTIC_REPLAY: PASS
```

## Phase 3 — Evidence and external replay

**Window:** 2026-09-13 to 2026-10-13

Deliverables:

- build a signed evidence pack from immutable source commits;
- reproduce the golden path in a second clean environment;
- publish limitations and failed cases beside successful results;
- create a versioned release only after replay succeeds;
- update public surfaces to show exact maturity, not aspirational status.

Evidence pack contents:

```text
SOURCE_REGISTRY.json
ENVIRONMENT.json
INPUT_HASHES.json
COMMANDS.txt
TEST_RESULTS.json
LEDGER.jsonl
REPLAY_REPORT.json
CLAIMS.json
SHA256SUMS
```

Exit gate:

```text
SECOND_ENVIRONMENT_REPLAY: PASS
EVIDENCE_PACK_COMPLETE: PASS
PUBLIC_CLAIMS_MATCH_EVIDENCE: PASS
RELEASE_CANDIDATE: PASS
```

## Operating metrics

Track only metrics that can be computed from retained artifacts:

- integrated golden-path coverage;
- test pass rate;
- deterministic replay rate;
- policy coverage by risk class;
- human override rate;
- mean recovery time from a failed run;
- active work in progress;
- number of externally reproduced runs;
- count of unsupported claims remaining.

## Stop conditions

The roadmap pauses and enters `BLOCK` when:

- a secret or private key is exposed;
- a production or scientific claim exceeds its evidence;
- a canonical interface changes without migration and rollback;
- execution cannot be reproduced from retained inputs;
- a repository duplicates a canonical organ without an explicit replacement decision;
- a destructive action is proposed without an independently tested restore path.
