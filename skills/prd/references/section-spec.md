# PRD section contract

Nine fixed sections in fixed order, plus one `Capability N — Name` section per capability and an instrument section wherever a judgment is made. Headings are exact: they are the anchors the TRD cites (`PRD §Capability 2`, `PRD §Non-functional · Privacy`, `PRD §Scope`, `PRD §Open questions`), and `scripts/lint_prd.py` checks them. Each entry says what the section is for, what it contains, and the pass test to meet before moving on.

Contents: §0 Header · §1 Summary · §2 Problem and goals · §3 Users and personas · §4 Capability N — Name · §5 Instrument sections · §6 Architecture · §7 Non-functional requirements · §8 Metrics and success criteria · §9 Scope, phases, and release plan · §10 Risks and open questions · Cross-section tests

---

## §0 Header

- H1: `# PRD — <Product name>`
- Byline, one line: `<Mon D, YYYY> · <author> · v<major.minor>`

The version is what the TRD's byline will trace to. A PRD that changes after the TRD is written bumps the version, so the mismatch is visible.

## §1 Summary

Purpose: the whole product in one screen — what it is, for whom, and the principle it is built on.

Contains:

1. One paragraph: what the product turns into what (*turns the 41-chapter reference into a SaaS where readers…*), the three to five things a user does, and the design principle in one clause (*built on its own harness*). Written so a reader who stops here knows the product.
2. A one-line lead-in that counts the structure (*Four capabilities, one content model, one audit trail:*).
3. The capability table: `Capability | What the user does | What the system guarantees`. One row per capability, same names and order as the §4 sections. *What the system guarantees* is the commitment — the sentence §7, §8 and §10 derive from. A row whose guarantee is a feature restated (*users can search*) has no guarantee yet.

Pass: the table's row count equals the number of Capability sections; every guarantee cell states something checkable (*every number links to its derive script*; *refuses outside the corpus*).

## §2 Problem and goals

Purpose: why this, why now, and what "worked" will mean at a fixed date.

Contains:

1. Problem paragraph: what is wrong today, stated with facts the reader can check (*34 labs reproduce their chapters' numbers, but a PDF hides both*). Name who suffers and what they cannot do.
2. `Goals, measurable at <horizon> after launch:` and the goals table: `Goal | Target | Measure`. *Target* is a number with a unit and a comparison; *Measure* names the ratio or report that produces it. Three to six rows.
3. `Non-goals:` one sentence listing what this product is not, each item a plausible thing a reader might assume (*a general AI chat product; a hosted agent platform; a marketplace*).

Pass: every goal row has a numeric target and a named measure; the non-goals sentence exists and lists ≥ 2 items.

## §3 Users and personas

Purpose: who the product serves, what each needs, and the account model.

Contains:

1. One sentence: persona count and where the set comes from (reading paths, roles in the workflow, buyer vs user).
2. Persona table: `Persona | Who | Primary use | Must have`. *Who* is a job title or role at a kind of organisation; *Must have* is what the product fails without for this persona — the TRD maps it to screens and components.
3. Account model paragraph: organisational vs individual accounts; identity requirements and the reason (*anonymous suggestions are not accepted, because provenance is part of the evidence*).

Pass: every persona has a non-empty *Must have*; every persona appears in at least one capability's requirements.

## §4 Capability N — Name

One section per capability, numbered from 1, in the order a user meets them and the order the phases ship them.

Contains:

1. One paragraph: what the capability is, in the product's own terms; what it is built from or modelled on (a reference component, a standard); what it is not (*not a general chat model*).
2. Optional diagram: a Mermaid `flowchart` when the capability is a pipeline with branches (intake → sensors → judgment → outcomes), followed by a one-line principle (*the agent's score decides only what the rubric can decide; a curator decides the rest*).
3. `Requirements:` a bullet list, 5–12 bullets. Each bullet is a **testable requirement**: a behaviour, its condition, and the observable outcome, with numbers where a number exists (*rationale ≤ 200 words*; *declined three times in a month is throttled and told why*). Guarantees are phrased as what the system does to a violation (*a claim with no citation is replaced by "the book does not cover this"*), not as aspirations.
4. Closing constraint line: `Limits:` or a sentence naming the boundary (*no GPU labs in the browser tier*; *no content is edited in the SaaS outside the improvement flow*).
5. Optional `Screens:` line with stable screen IDs (`Report-Draft, Finding-Detail`) when the product has a UI package or one will be made; the TRD maps every ID to a route.

Pass: ≥ 5 requirement bullets; at least one bullet carries a number; the refusal or failure behaviour of the capability is stated; every persona that uses it is named or implied by a requirement.

## §5 Instrument sections

Present wherever a capability has a model or a person make a judgment (grade, score, adjudicate, approve, rank, classify with consequences). The PRD does not say *the agent decides*; it publishes the instrument the decision uses. Name the section for the instrument (*Evidence grading rubric*, *Approval policy*, *Priority scoring*). Place it after the capability it serves.

Contains:

1. One paragraph: the scoring principle (tiered base score, then multiplicative adjustments; *the strongest item's adjusted score, not the sum, so ten weak items never equal one strong one*) and what the tiers extend or derive from.
2. Tiers table: `Tier | Examples | Base score`. Each tier letter-coded with ≥ 2 concrete examples; the bottom tier is *Unverifiable* at 0, so an unopenable source is never graded as merely weak.
3. Adjustments table: `Factor | Rule | Multiplier`, each factor with its levels and the value per level.
4. Thresholds table: `<Class> | Accept ≥ | Floor (decline below)`, one row per decision class, with a *human always* class for what the instrument must not decide (safety, structure, the instrument itself).
5. `Worked examples:` three to five bullets, each a realistic case with the arithmetic written out and the outcome named (*70 × 1.0 × 1.0 × 0.8 = 56 < 70 → request more*). At least one example lands between floor and threshold, and one shows a human override being recorded.
6. Versioning sentence: the instrument is versioned and published; changing it is a human-only class and is announced.

Pass: the three tables are present; every worked example's arithmetic is correct; the human-always class exists.

## §6 Architecture

Purpose: the constraints and the mapping the TRD will work within — not the component picks, which are the TRD's.

Contains:

1. Principle sentence: what the product is built on and where the design documents are (*the book's chapters are the design documents*; *the platform's ADRs*).
2. Mapping table: `Product component | <Reference> component | Role in the product`. One row per product part, each naming the reference it implements (chapter, ADR, standard) and its role in one line. When no reference corpus exists, the middle column is `Pattern` and names the well-known pattern (gateway, control plane, policy engine, ledger).
3. Pipeline paragraph: source of truth, release model, how changes flow back, the regression gate.
4. Deployment paragraph: tenancy, isolation of untrusted compute, where model calls go, residency with the regulation that requires it.

Pass: every capability's components appear in the mapping table; the source of truth is named; residency is stated.

## §7 Non-functional requirements

Table: `Area | Requirement`. Rows, in this order, so the TRD can cite `§Non-functional · <Area>`: `Security`, `Privacy`, `Cost control`, `Performance`, `Availability`, `Accessibility`, `Languages`, `Auditability`, `Content integrity`. Drop a row only with a one-line reason in its cell. Each cell lists the concrete requirements separated by `;` with numbers (*chapter load < 1 s; search < 500 ms*; *99.5% for reading; 99% for IDE*; *retained 30 days as text*).

Pass: every row has a number or a named standard (WCAG 2.2 AA, LGPD); no cell says *high*, *fast*, *secure* or *scalable* without a value.

## §8 Metrics and success criteria

Contains:

1. Lead-in: *<N> headline numbers, reviewed <cadence>; the rest are leading indicators.*
2. Headline table: `Metric | Definition | Target at <horizon>`. Three to five rows; *Definition* is a ratio or count a dashboard can compute.
3. `Leading indicators:` one sentence listing them, each with its threshold and the action it triggers (*override rate per criterion, target < 10%; above 20% triggers a rubric review*).
4. `What is not measured:` the metrics deliberately absent and the one reason (*each rewards volume over evidence*).

Pass: every headline metric traces to a §2 goal; every leading indicator with a threshold names what happens when crossed; *What is not measured* lists ≥ 2 items.

## §9 Scope, phases, and release plan

Contains:

1. Principle sentence: *<N> phases, each shippable, each adding one capability on the previous one's <foundation>.*
2. Phase table: `Phase | Ships | Gate to next`. One row per phase; *Ships* lists what the phase delivers; *Gate to next* is numeric and checkable (*citation rate ≥ 90% on a 300-question golden set*). The TRD copies these gates into its own phase table.
3. `Out of scope for the first release:` one sentence.
4. `Dependencies:` one sentence naming each external dependency with its current state (*currently 35 drafted, 34 labs reproducing*).

Pass: every phase has a numeric gate; the phase order matches the capability order; out of scope and dependencies are present.

## §10 Risks and open questions

Contains:

1. Risk table: `Risk | Mitigation`. One row per risk that would make a goal miss; the risk names the mechanism of failure (*contributors cite tier-B sources that do not say what they claim*), the mitigation names the control, the detection and the consequence (*relevance graded with the source opened; curators sample monthly; misattribution throttles the account*). The TRD turns each row into an attack/control/detection/residual row.
2. `Open questions:` bullets. Each is a decision not yet made, written with its options (*seats per organisation, individual tier, or usage-metered?*). The TRD answers each with an assumption and what changes otherwise. A worry with no decision in it is not an open question; it is a risk.

Pass: every risk mitigation names a mechanism, not an intention; ≥ 3 open questions, each phrased as a choice.

---

## Cross-section tests

Run after the draft, before lint:

- **Guarantee.** Every §1 capability guarantee is backed by at least one §4 requirement bullet that says what the system does when the guarantee would be violated.
- **Goal → metric.** Every §2 goal has a §8 headline metric or leading indicator that measures it, with the same number.
- **Persona → requirement.** Every §3 persona's *Must have* is satisfied by a named requirement in some §4 section.
- **Number.** Every goal target, NFR, metric target, phase gate and threshold is a number or a named standard. The words *fast*, *robust*, *scalable*, *user-friendly*, *appropriate* and *reasonable* are replaced by the value they were hiding.
- **Instrument.** Every judgment (grade, approve, adjudicate, rank) has an instrument section with worked examples whose arithmetic you have redone.
- **Mechanism.** Every risk mitigation and every guarantee names the mechanism (sensor, cap, policy, sample, throttle), and the reference it comes from when a corpus exists.
- **Boundary.** Non-goals, out of scope, limits per capability, and *what is not measured* are all present. A PRD that only says what the product does leaves the TRD to guess what it must not do.
- **Decision.** Every open question is a choice with options; everything the PRD assumed without deciding is listed there.
- **Closure.** `TBD`, `TODO`, `TBC`, *to be defined* do not appear; an unknown is an open question.
- **Anchor stability.** Section headings match this contract exactly; NFR rows use the fixed area names; capabilities are numbered 1..N in phase order. The TRD's anchors resolve against these.
