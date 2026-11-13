---
name: trd
description: Technical stage of the Tank Factory Architect (Tech Lead hat) — write or amend the product's living TRD at docs/trd/<product>.md, traced to the PRD, with the Stack section, C4 diagrams, component map and invariants, network topology, MER, data flow, endpoint map, integration sequences, AI orchestration, MLOps, DevOps, security, testing and open decisions. Use for a new product's TRD, a TRD amendment, an as-built TRD of an adopted codebase, or whenever someone asks for a technical spec, architecture document, data model, API contract or deployment topology for a product that has a PRD.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# trd

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Tech Lead | technical (`brief_to_backlog/*`), as-built TRD (`adopt_repository`), revision | `docs/trd/<product>.md`; in amendment mode the shared `docs/initiatives/<id>/impact.md` | TRD lint 0 fail; every endpoint typed; every invariant maps to ≥ 1 check; `stack_profile` gate | tech lead, after the Critic (Spec) scores it |

The TRD turns the PRD's *what* into a *how* that agents can build without guessing: which pieces exist, where each lives, what may call what, and what must always hold. Every section is **traced** — it names the PRD line it serves — and a section that only restates the PRD is deleted. The Planner will read single sections by heading, so each one stands on its own.

## Inputs

- The approved PRD (ids, objects, screens, NFR rows) and the research report (support systems, constraints).
- The factory guardrails and supported stacks (`environment.yaml`), for the Stack section.
- Brownfield, amendment and as-built: the graph, `main`, and the living TRD at its approved SHA.

## Steps

1. **Read the PRD for obligations.** List every `FR-`, every NFR row, every object and every support system. Done when each is assigned to the section that will answer it.
2. **Choose the stack** (§2) with the `stack-profile` skill, inside the guardrails and the supported stacks. Done when the profile block passes its lint.
3. **Fix the shape**: C4 diagrams (§3), then the component map with its import rules and the invariants (§4). Done when every container has components, every component a folder, and there are ≥ 4 invariants, each naming the check file that will prove it.
4. **Fix the contracts**: network (§5), MER (§6), data flow (§7), endpoint map (§8), integration sequences (§9). Done when every PRD object has an entity, every endpoint has a request and a response type defined in §8.1, and every external system has a sequence with its failure branch.
5. **Fix run and intelligence**: AI orchestration (§10), MLOps (§11), DevOps (§12), security (§13), testing (§14). A product with no model call writes `None: <reason>` in §10 and §11.
6. **List what is not decided** (§15) as choices with the option you assumed.
7. **Self-check.** `python3 scripts/lint_trd.py docs/trd/<product>.md --prd docs/prd/<product>.md [--research docs/research/<brief>.md] [--mode new|amendment|as-built]`. Done at 0 fail.
8. **Hand over**: the `tech-lead-evals` skill writes the checks §4.1 names; then return the envelope with `phase: technical`, artifacts `trd` (or `trd_amendment`, `impact`) and `tech_evals`, and the `stack_profile` copied from §2.

## Shape

Start from `assets/trd-template.md`; `references/exemplar.md` is a passing TRD. Headings are exact and numbered; other artifacts cite them as `TRD §8. Endpoint map`. Diagrams are Mermaid text, so agents can read and diff them.

| Section | Contains | Pass test |
| --- | --- | --- |
| `# TRD — <Product>` + byline | date · version · mode · `traces to PRD v<x.y>` | present |
| `## 1. Purpose, scope, phases` | one paragraph; table `Phase \| Adds \| Gate`; the traceability rule | gates are numbers from the PRD |
| `## 2. Stack` | table `Choice \| Pick \| Alternatives \| Why`; the `stack_profile` JSON block; `Guardrail requests:` | profile block parses (`stack-profile` skill) |
| `## 3. C4 diagrams` | `### 3.1 System context` (`C4Context`), `### 3.2 Containers` (`C4Container`), `### 3.3 Components` of the core container | actors and external systems named as in the PRD and research; every arrow labelled |
| `## 4. Component map` | table `Component \| Repository \| Folder \| Responsibility \| May import \| Never imports`; `### 4.1 Invariants`: `ID \| Invariant \| Check \| Serves` | every folder named; ≥ 4 invariants `INV-n`, each with a check path under `evals/tech/` |
| `## 5. Network topology` | Mermaid flowchart with a port on every edge; table `From \| To \| Protocol · port \| Auth \| Notes`; environments, regions, residency, egress allow-list | every conduit has a port and an auth value |
| `## 6. Data model (MER)` | Mermaid `erDiagram` with typed attributes and cardinalities; table `Entity \| PRD object \| Keys \| Indexes \| Retention` | every PRD object has an entity; every attribute has a type |
| `## 7. Data flow` | table `Object \| Created \| Stored \| Sent to \| Deleted \| Personal data` | every object with personal data has a deletion path |
| `## 8. Endpoint map` | table `Method \| Path \| Roles \| Request \| Response \| Errors \| Idempotency \| Rate limit \| Serves`; `### 8.1 Types` with every named type in a code block | request and response name a type defined in §8.1 (or `—` for no body); `Serves` cites an `FR-` id |
| `## 9. Integration sequences` | table `Integration \| System \| Direction \| Auth \| Timeout \| Retries`; one `sequenceDiagram` per row | each diagram has an `alt` failure branch; each timeout is a number |
| `## 10. AI orchestration and protocols` | table `Call \| Model tier \| Prompt \| May read \| May never read \| Tools \| Output schema \| Checks before \| Checks after \| Cap`; table `Protocol \| Used for \| Auth` | every call has an output schema and a numeric cap; or `None: <reason>` |
| `## 11. MLOps` | table `Call \| Reference set \| Metric \| Gate \| Cadence \| Drift monitor \| Retirement`; a `Versioning:` line | every §10 call has a row with a numeric gate; or `None: <reason>` |
| `## 12. DevOps` | table `Environment \| Purpose \| Deploys from \| Data`; `Pipeline:` stages; `Rollback:` with a time; table `SLO \| Alert \| Threshold` | rollback has a number; every availability and performance NFR has an alert |
| `## 13. Security and threat model` | table `Threat \| Path \| Control \| Check`; table `Secret \| Lives in \| Reachable by` | every threat has a control |
| `## 14. Testing` | table `Layer \| What \| Where \| Runs` | names feature bindings, conformance checks, unit and integration tests |
| `## 15. Open decisions and assumptions` | table `Decision \| Options \| Assumed \| Owner \| Needed by` | every row has an assumed option |

Each of sections 2–14 opens with the PRD anchors it serves, in one line: `Serves: PRD §Capability 1 — Reading capture (FR-1.2, FR-1.3); PRD §Non-functional requirements · Availability`.

**Invariants are promises with a proof.** An invariant is a statement that must hold on every commit (`a reading id is stored at most once`). Each names the file under `evals/tech/` that fails when it is broken; at least four, because the context gate requires them and the Reviewer judges diffs against them.

**The component map is the boundary law.** `Folder` is where the component lives; `May import` and `Never imports` become import contracts the boundary-check tool enforces, and build-plan units are cut along these folders — one boundary per unit.

## Modes

- **new**: the whole document, `v1.0`.
- **amendment**: edit the living TRD in place; keep headings and ids; add to `impact.md` the sections changed, units affected and ADRs touched. A new language, framework or major version is a Stack change and re-enters the `stack_profile` gate.
- **as-built**: describe the architecture that exists. Add a `Code` column to the component map, the entity table and the endpoint map, each cell a path in backticks; record the stack in use; mark anything inferred as `inferred` with its evidence.

## Checklist the tech lead signs

- Every endpoint typed.
- Every invariant maps to ≥ 1 check.
- Each stack is a supported stack inside the factory guardrails, or each need is in `guardrail_requests[]` with its reason.
- `product_kind` agrees with the PRD's screens.
- As-built: every language, package manager and version matches the manifests and lockfiles.

## Limits

Writes only `docs/trd/**`, `docs/initiatives/**` and `docs/adr/**`. A requirement the PRD does not state becomes a row in §15 or a question to the product owner, never invented behaviour. Two gate corrections, then `blocked(doc_lint)` with the lint output.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
