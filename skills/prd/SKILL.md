---
name: prd
description: Write a Product Requirements Document (PRD) — summary with guarantees per capability, measurable goals, personas, testable requirements per capability, the scoring instrument behind any automated or human judgment, architecture mapping, non-functional rows, metrics, phases with numeric gates, risks and open questions — in the fixed shape a TRD traces to. Use this whenever the user asks for a PRD, product requirements, a product spec, "what should this product do", to turn a brief, pitch, research notes or a conversation into requirements, to add a capability to an existing PRD, or says "/prd". Also use it when the user asks for goals and metrics, personas, or a phase plan for a product on their own — those are PRD sections and should be written to the same contract so the TRD skill can cite them.
---

# PRD

A PRD is the document a TRD traces to. Every section of the TRD cites a PRD line, so the PRD's job is to be citeable: fixed headings, numbered capabilities, a guarantee per capability, numbers on every goal, gate and non-functional row, and an explicit list of what is not decided. The reader is an engineer who will take each requirement as a test and each open question as an assumption to make, and a sponsor who will take each goal as a promise.

The standard is `references/exemplar.md` (the PRD for a four-capability, model-backed SaaS; `trd` skill's exemplar was written from it). Read its Summary and one Capability section before drafting; read the matching section in full when drafting each of yours.

## Inputs

| Input | Status | What to do without it |
| --- | --- | --- |
| Brief, pitch, idea, research notes, or the conversation so far | required | A one-line idea is enough to start the interview, not enough to write. |
| Who it is for and what they cannot do today | required | Ask. The problem paragraph needs checkable facts, not a premise. |
| Capabilities (≤ 5 for a first release) and the guarantee each must hold | ask | Propose from the brief; confirm. The guarantee column is the spine of the document. |
| Constraints: stack, residency, regulation, budget, deadline | ask once | They go in Architecture and Non-functional requirements and are never re-opened downstream. |
| Design reference corpus (a book, ADRs, standards) | optional | The Architecture mapping table cites it; without one the middle column names the pattern. |
| Existing PRD | when extending | Read it whole; keep its headings and numbering; bump its version. |

**Interview before writing** when the brief leaves any required row empty. Ask in one pass (`AskUserQuestion` when present, otherwise a short numbered list): the problem with its evidence; the personas and each one's must-have; the capabilities with the guarantee each must hold; non-goals; the horizon for goals and the targets the sponsor would sign; the phase order; what is already decided. If the user says to proceed anyway, draft with every unconfirmed value marked in the open questions, never silently invented — a fabricated target reads as a promise.

## Workflow

1. **Write the Summary capability table first** — `Capability | What the user does | What the system guarantees` — and get it right before anything else. Every later section elaborates a row of it: requirements enforce the guarantee, metrics measure it, risks threaten it, phases ship it. Done when every guarantee cell is a checkable statement, not a feature restated.
2. **Draft the fixed sections in order** from `assets/prd-template.md`, with `references/section-spec.md` open at the section being written. Headings are exact (they are the TRD's anchors); each section has a pass test; meet it before the next. Done when the template has no placeholder left.
3. **Write an instrument section for every judgment.** Wherever a capability has a model or a person grade, score, approve, adjudicate or rank, the PRD publishes the instrument: tiers with base scores, multiplicative adjustments, thresholds per decision class with a *human always* class, and worked examples with the arithmetic written out. Done when you have redone each example's arithmetic and one example lands between floor and threshold.
4. **Cross-section tests** (end of `section-spec.md`): guarantee, goal → metric, persona → requirement, number, instrument, mechanism, boundary, decision, closure, anchor stability. Done when each passes on a re-read.
5. **Lint.** `python3 scripts/lint_prd.py <file>`. Fix every FAIL; treat each WARN as a question — most are a hidden number or a boundary not yet stated. Done at 0 fail.
6. **Deliver** in the environment's native form: a doc when a docs connector is present (the exemplar lived as one), else `docs/prd/<product>-prd.md` in the repository. Close with the open questions — they are what the sponsor must answer and what the TRD will assume — and offer the `trd` skill as the next step.

## Rules that hold across every section

- **Guarantees, not features.** A capability is described by what the system guarantees and what it does when the guarantee would be violated (*a claim with no citation is replaced by "the book does not cover this"*). A list of things users can do is a feature list, not a requirement.
- **Numbers, not adjectives.** Goal targets, non-functional rows, metric targets, phase gates, thresholds and rate limits are values with units (*< 500 ms*, *≥ 90% on a 300-question golden set*, *≤ 200 words*, *three times in a month*). *Fast*, *robust*, *scalable* and *appropriate* are the lint's vagueness warnings for a reason: each hides a number someone will have to invent later.
- **Testable requirements.** Each bullet names a behaviour, its condition and the observable outcome. If a tester could not write a pass/fail case from the bullet, split it or add the number.
- **Instruments are published.** The PRD never says *the agent decides*; it shows the rubric, the thresholds, the worked examples, the human-always class, and that the instrument is versioned and changes are announced. This is what makes an automated decision auditable and a human override meaningful.
- **Mechanism beside every mitigation.** A risk's mitigation names the control, where it is detected, and the consequence (*graded with the source opened; curators sample monthly; misattribution throttles the account*). An intention (*we will monitor this*) is not a mitigation.
- **Boundaries are explicit.** Non-goals, limits per capability, out of scope for the first release, and *what is not measured* with the reason. A PRD that only says what the product does leaves the TRD to guess what it must not do.
- **Reference the design corpus.** When a book, ADR set or standard exists, every mechanism names the one it implements (*ch26*, *ADR-014*, *WCAG 2.2 AA*). The TRD's component picks cite the same sources.
- **The PRD maps roles; the TRD picks components.** Architecture here is the mapping table, the source of truth, the release model, tenancy and residency — not vendor choices. A PRD that names Postgres and Temporal has started writing the TRD.
- **Open questions are decisions.** Each is phrased as a choice with its options (*seats, individual tier, or usage-metered?*). A worry with no decision in it belongs in the risk table.
- **One spelling convention, kept.** The TRD will follow it verbatim, down to persona names and capability titles.

## Extending an existing PRD

Keep the headings and the capability numbering; a new capability takes the next number and its phase row. Add a Summary table row, a persona *Must have* if a new persona appears, the capability section, an instrument section if it judges, mapping-table rows, any new non-functional requirement inside the existing area rows, a headline metric or leading indicator, a phase row with a gate, risk rows, and open questions. Bump the version (minor for a capability, patch for a corrected number) — the TRD's byline will show the mismatch until it is updated.

## Where things live

- `references/section-spec.md` — the per-section contract: exact headings, table columns, pass tests, cross-section tests. The authority when this file and your memory disagree.
- `references/exemplar.md` — a full PRD meeting the standard. Copy its shapes, not its product.
- `assets/prd-template.md` — the skeleton. Start every new PRD from it.
- `scripts/lint_prd.py` — headings, columns, numbers, instruments, boundaries, open questions, arithmetic in worked examples, closure. Run before any review.
