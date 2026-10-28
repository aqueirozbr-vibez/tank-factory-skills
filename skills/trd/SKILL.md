---
name: trd
description: Write a Technical Requirements Document (TRD) from a PRD — the architecture, data model, API contract, network, agents, security, testing and open decisions, every section traced to the PRD line it serves. Use this whenever the user asks for a TRD, a technical spec, a system design doc, an architecture document, "the technical side of the PRD", C4 diagrams plus a schema, or to extend or review an existing TRD — even if they only say "spec this out technically", "turn the PRD into something engineering can build from", or "/trd". Also use it when a PRD exists and the user asks for the data model, endpoint catalogue, or deployment topology on their own; those are TRD sections and should be written to the same contract.
---

# TRD

A TRD is the document engineering builds from. It carries what the PRD does not: the picks, the schema, the ports, the limits, the failure branches, and the decisions nobody has made yet. Its reader is a senior engineer who will not re-derive anything, so every section must be concrete enough to code against and traced to the PRD line that justifies it.

The standard is set by `references/exemplar.md` (a complete TRD for a four-capability, model-backed SaaS). Read its §1 and skim its headings before the first draft; read any section of it in full when drafting the matching section.

## Inputs

| Input | Status | Why |
| --- | --- | --- |
| PRD | required | Every section anchors to it. Without a PRD there is nothing to trace to — stop and ask for it, or offer to write the PRD first. A one-paragraph idea is not a PRD. |
| UI package / screen list with IDs | strongly preferred | §2.3 and §5.1 map every screen to a capability and a route. Without one, derive screen names from the PRD's capabilities and say in §12 that the UI package is assumed. |
| Fixed stack | ask once | What is already decided (framework, database, cloud) goes in §1 and is never re-opened in §2.0. |
| Design reference corpus | optional | ADRs, a book, standards, vendor docs. Each §2.0 pick and each §10 control cites the one it implements in its *Source* column. |
| Existing TRD | when extending | Read it whole; keep its numbering; add rows and sections; update §12. |

Read the PRD in full before writing anything. Pull out, as a scratch list with IDs: capabilities (C1…), personas, non-functional rows (NFR: performance, privacy, security, auditability…), screen IDs, phases and gates, metrics and "what is not measured", risks or named attacks, open questions. This is the **traceability ledger**; every entry gets ticked by at least one TRD section before the document is done.

## Workflow

1. **Decide before drawing.** Fill §2.0 Component decisions first — every component outside the fixed stack, ≥ 2 candidates, the pick, the disqualifier of the loser, the source it implements. Diagrams draw picks, not categories; a diagram drawn before this table shows boxes called "cache" and "queue" that nobody can build. Done when every PRD capability can be delivered by some combination of fixed stack + picks.
2. **Draft §1 → §12 in order** from `assets/trd-template.md`, with `references/section-spec.md` open for the section being written. Each section has a stated pass test; meet it before starting the next. Diagrams follow `references/diagram-patterns.md` (Mermaid only, invariant paragraph after each). Done when the template has no placeholder left and every ledger entry is ticked.
3. **Cross-section tests** (the list at the end of `section-spec.md`): restatement, anchor, number, candidate, mechanism, closure, coverage. Delete any section that only restates the PRD — the §1 rule says so in the document itself, and a reviewer will apply it. Done when every test passes on a re-read.
4. **Lint.** `python3 scripts/lint_trd.py <file>` (add `--no-agents` when §8 is the one-line "no model-backed components"). Fix every FAIL; treat each WARN as a question and either fix it or decide it is right. Done at 0 fail.
5. **Deliver** in the environment's native form: a doc when a docs connector is present (the exemplar lived as one), else `docs/trd/<product>-trd.md` in the repository. Close with the §12 review list and one sentence on what the PRD left open that the TRD decided — that list is what the reviewer reads first.

## Rules that hold across every section

- **Traceability.** Every H3 heading carries its anchor in parentheses — `(PRD §Capability 2)`, `(PRD §Non-functional · Privacy)` — or the section's intro cites one. A section tracing to nothing is deleted, not kept for completeness.
- **Numbers, not adjectives.** Budgets, limits, retention, thresholds, gates and caps are values: `< 500 ms`, `20/min/user`, `30 days`, `κ ≥ 0.7`, `cap 1`. "Fast", "reasonable" and "appropriate" do not appear.
- **Mechanism beside every rule.** A rule the product enforces names the field, constraint, policy, workflow refusal or scanner that enforces it. "By convention" is an admission there is no mechanism.
- **Fail-closed.** Every decision point (policy engine, gateway, orchestrator, webhook signature) states what it does when unreachable or invalid, and the answer is deny, refuse or discard. §10 ends with this paragraph; the authorisation diagram in §6.2 draws the unreachable edge.
- **Sensors before judgment.** Where a model or a human judges, cheap deterministic checks run first and every outcome — including the declines that never reached the model — lands in the audit record. The pipeline flowchart in §2.3 and every §7 sequence make this visible.
- **Residual risk is never empty.** A control with nothing left over is a control nobody examined.
- **Unknowns become §12 rows**, each with the assumption used and what changes if decided otherwise. `TBD` and `TODO` are lint failures.
- **Tables carry decisions; prose carries invariants.** After every diagram, one paragraph (≤ 3 sentences) says what the diagram guarantees and what a user never sees. Column headers in `section-spec.md` are exact — the lint checks them.
- **Spelling and terms follow the PRD.** If the PRD writes *organisation* and *authorise*, so does the TRD; its personas, capability names and screen IDs are used verbatim.

## When the product has no model-backed component

§8 becomes the single line *No model-backed components in this release.* and keeps its number, so section references stay stable across the product's TRDs. §3.4 keeps its secrets table but drops the *Proof* paragraph's prompt-scanner clause; §6.3 covers whatever is metered (compute minutes, storage) or states that nothing is.

## Extending an existing TRD

Keep the file's numbering and table shapes. A new capability adds: a §1 phase row or an edit to one, §2.0 rows for any new component, a §2.3 row, §3.1 conduits, §4 entities and rules, §5.1 routes, §6.1 endpoints, one §7 sequence, a §10 row for each new attack surface, and §12 rows for what it leaves open. Append to the "Decisions this document made" list rather than rewriting it. Bump the byline version (minor for a capability, patch for corrections).

## Where things live

- `references/section-spec.md` — the per-section contract: required tables with exact columns, diagram kinds, pass tests, and the cross-section tests. The authority when this file and your memory disagree.
- `references/diagram-patterns.md` — Mermaid skeletons for C4 context, containers, deployment, topology, ERD, pipeline, sequence, authorisation and integrations, with the conventions each must keep.
- `references/exemplar.md` — a full TRD meeting the standard. Copy its shapes, not its product.
- `assets/trd-template.md` — the skeleton. Start every new TRD from it.
- `scripts/lint_trd.py` — structure, columns, diagrams, failure branches, anchors, closure. Run before any review.
