# MatVerse Operational Control Charter

**Effective date:** 2026-07-15  
**Status:** PROPOSED_ACTIVE_ON_BRANCH  
**Constitutional owner:** Mateus Alves Arêas / MatVerse-py  
**Operational mode:** consolidation, verification and controlled execution

## 1. Mission

MatVerse is governed as one computational organism whose purpose is to mediate the path between human or agent intent and externally effective action through explicit policy, risk control, traceability and replay.

Canonical flow:

```text
INTENT -> CASSANDRA -> CRITICAL LENSES -> OMEGA-GATE -> ORGANISMO -> LEDGER -> REPLAY -> PROOF
```

No repository, module, agent, paper or interface may override this flow by narrative declaration.

## 2. Authority boundaries

- The founder retains constitutional, legal, credential and production authority.
- Automated or delegated operators may inspect, classify, test, create branches, propose patches and open pull requests.
- No delegated operator may expose secrets, rotate credentials, deploy to production, delete repositories, rewrite protected history or merge sensitive changes without an explicit reviewed gate.
- Repository text is not evidence of deployment, scientific validation or production maturity.

## 3. Ninety-day expansion freeze

From 2026-07-15 through 2026-10-13:

- no new framework, organism, acronym or top-level repository unless it closes a verified capability gap;
- no renaming of canonical organs without a migration record;
- no new performance, TRL, scientific, production or institutional claim without a linked evidence pack;
- new ideas are recorded under `INCUBATOR`, not promoted into the canonical runtime;
- work in progress is limited to one objective, three deliverables and five active tasks per execution cycle.

## 4. Canonical organs

| Organ | Canonical function | Primary repository |
|---|---|---|
| Constitution | invariants, definitions and normative boundaries | `matverse-acoa/core` |
| Control plane | policy orchestration, context and administrative control | `matverse-acoa/Cassandra` |
| Decision gate | binary or escalated authorization before effects | `matverse-acoa/Gate` |
| Runtime organism | execution, state transition and recovery | `matverse-acoa/Organismo` |
| Scientific layer | formalization, methods and publishable evidence | `matverse-acoa/papers` |
| Laboratory | hypotheses and experiments that cannot claim production authority | `matverse-acoa/QEX` |
| Experience surface | read-only projection and human interaction | `matverse-acoa/CUBE` |
| Control registry | portfolio map, status, claims and cross-repository governance | `matverse-acoa/matverse` |
| Evidence store | test outputs and reproducibility artifacts | `matverse-acoa/mvo-test-results` |

Other repositories are dependencies, incubators, products or historical artifacts until explicitly admitted by the registry.

## 5. Maturity states

Only the following states are permitted:

1. `CONCEPT` — idea or narrative only.
2. `SPECIFIED` — contracts or documentation exist.
3. `EXECUTABLE` — code runs in a declared environment.
4. `TESTED` — automated tests pass with retained outputs.
5. `INTEGRATED` — the canonical end-to-end flow executes.
6. `EXTERNALLY_VALIDATED` — an independent environment reproduced the result.
7. `PRODUCTION` — a maintained deployment has users, monitoring, rollback and incident handling.
8. `ARCHIVED` — preserved as history and removed from active priority.

A higher state requires evidence for every lower state. Missing evidence forces `HOLD`.

## 6. Critical lenses

Every material change must be assessed by the following complementary controls:

- `TRUTHMODE`: separate observation, inference and claim.
- `REDTEAM`: test failure, abuse and adversarial paths.
- `UNLEARN`: identify obsolete assumptions and duplicated architecture.
- `80/20`: preserve the smallest path that proves the organism.
- `HORMOZI`: require concrete user or operational value.
- `FUTUREYOU`: examine long-term lock-in, debt and reversibility.
- `/human`: preserve human authority, dignity and comprehension.
- `H-AXIS`: prevent narrative coherence from being treated as factual truth.

## 7. Change control

Every canonical change must include:

- problem statement;
- evidence and uncertainty;
- affected invariants;
- minimal reversible patch;
- tests executed and retained output;
- migration and rollback;
- final gate: `PASS`, `HOLD`, `BLOCK` or `ESCALATE`.

Direct pushes to canonical `main` branches are prohibited as an operating rule. Sensitive changes remain in draft pull requests until evidence is complete.

## 8. Golden path

The first system-level objective is one reproducible execution:

```text
request
-> normalized intent
-> Cassandra policy evaluation
-> critical-lens report
-> Omega-Gate decision
-> authorized or blocked action
-> append-only record
-> deterministic replay
-> evidence pack
```

No expansion is prioritized above this path.

## 9. Portfolio admission and apoptosis

A repository is admitted to the canonical organism only when it has a unique function, named interface, owner, tests and dependency map.

A repository is moved to `ARCHIVED` when it is duplicated, abandoned, superseded, untestable or unable to state a unique function. Archiving preserves history; it does not certify correctness.

## 10. Immediate directives

1. Correct unsupported maturity and institutional claims.
2. Establish the live portfolio registry.
3. Resolve open security-policy pull requests without merging stale fleet counts.
4. Finish one integrated golden-path execution.
5. Produce an evidence pack and replay it in a second environment.
6. Only then publish a release, paper claim or production statement.
