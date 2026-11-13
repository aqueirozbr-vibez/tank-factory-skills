---
name: prd
description: Product stage of the Tank Factory Architect (Product Owner hat) — write or amend the product's living PRD at docs/prd/<product>.md in the fixed shape with Principles, user roles, jobs to be done, journey flowchart, screens map, service blueprint, objects, numbered requirements and success criteria per capability, and non-functional rows. Use for a new product's PRD, a PRD amendment for an initiative or change request, an as-built PRD of an adopted codebase, or whenever someone asks for product requirements the TRD, UI and feature files can cite.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# prd

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Product Owner | product (`brief_to_backlog/*`), as-built PRD (`adopt_repository`), revision | `docs/prd/<product>.md`; in amendment mode also `docs/initiatives/<id>/impact.md` | PRD lint 0 fail; Principles ≤ 10 articles, each with its compliance check | product owner, after the Critic (Spec) scores it |

The PRD is the document everything downstream **cites**: feature files cite its success criteria, wireframes its screens, the TRD its requirements and objects, the build plan its capabilities. So the job is to be citeable: fixed headings, stable ids, one name per thing, a number on every target.

## Inputs

- The research report `docs/research/<brief>.md` and the answered discovery questions. Reuse its persona, step and system names verbatim.
- The brief's constraints and the factory's governance preset (they seed the Principles).
- Amendment: the living PRD at its approved SHA. As-built: the survey `docs/research/as-built.md`, the graph and `main`.

## Steps

1. **Fix the capabilities.** Write the Summary table first — capability, what the user does, what the system guarantees — and set `Product kind`. Done when every guarantee is a statement a test could falsify.
2. **Write the people blocks**: personas (from research), then User roles, then Jobs to be done. Done when every persona has a role and every job has a number that proves its outcome.
3. **Write Journeys and screens**: the future journey as a Mermaid flowchart whose nodes name screen ids, then the Screens map. Done when every screen in the map is on the flowchart, every screen id on the flowchart is in the map, and each screen's `Leads to` names the screens a user can reach from it (itself when the flow stays). Outcome nodes such as `Reading synced` need no screen. A product with no screens writes `No screens: service product.` in place of the flowchart and the map.
4. **Write the Service blueprint**: the future service, with the product in it, one row per step `B-n`. Start from the research's Customer blueprint and redraw each step as it will run: what the user sees (frontstage), what the product does out of sight (backstage), the support system involved, what can fail and how the service recovers, and the requirements that make the step happen. Done when every screen in the map is on a step, every support system in the research blueprint is on a step, every failure point has a recovery, and every step cites the `FR-` ids that deliver it. Fill that column once the capabilities exist (step 6); a step no requirement delivers means a requirement is missing.
5. **Write Objects**: every thing the product stores or shows, with typed fields and an example. Done when every object the Screens map names exists and every field has a type and an example.
6. **Write each Capability section**: features, requirements `FR-<cap>.<n>`, success criteria `SC-<n>` (numbered across the whole document, each naming the feature it tests), limits and the `Screens:` line. Done when a tester could write a pass or fail case from every requirement, every feature has ≥ 1 success criterion, and every refusal or failure a requirement names is covered by a criterion — the feature files are written from the criteria, so an uncovered refusal is never tested.
7. **Write Principles** (≤ 10 articles) from the brief's constraints and, when the factory has one, its governance preset. Each article names the check that shows compliance: `conformance check: <what it asserts>` (the TRD later gives it a file under `evals/tech/`), a Code health policy threshold, or `review question: <the question>`.
8. **Fill the remaining fixed sections** in order: Architecture (roles, not vendors), Non-functional requirements, Metrics and success criteria, Scope, phases, and release plan, Risks and open questions.
9. **Self-check.** `python3 scripts/lint_prd.py docs/prd/<product>.md --research docs/research/<brief>.md [--mode new|amendment|as-built] [--impact docs/initiatives/<id>/impact.md]` — the script is in this skill's folder; document paths are relative to the repository root. Done at 0 fail; read each WARN as a hidden number or a missing boundary.
10. **Return the envelope**: `phase: product` (or `as_built_prd`), artifact kind `prd` or `prd_amendment` (plus `impact`), and any question you could not close in `open_questions[]`.

## Shape

Start from `assets/prd-template.md`; `references/exemplar.md` is a passing PRD. H2 headings are exact and in this order — they are the anchors other artifacts cite as `PRD §<heading>`.

| Section | Contains | Pass test |
| --- | --- | --- |
| `# PRD — <Product>` + byline | date · version · mode · `traces to research <path>` (or `traces to brief <id>` when there is no report) | date, `v<major>.<minor>` and `traces to` present |
| `## Summary` | 1–2 paragraphs; `Product kind: ui \| service \| ui_and_service`; table `Capability \| What the user does \| What the system guarantees` | one row per Capability section |
| `## Problem and goals` | problem with sourced facts; table `Goal \| Target \| Measure`; `Non-goals:` | every target has a number |
| `## Principles` | table `Article \| Principle \| Compliance check`, articles `P-1` … | ≤ 10 rows; no empty check |
| `## Users and personas` | table `Persona \| Who \| Primary use \| Must have`; `### User roles`: `Role \| Personas \| Permissions \| Never`; `### Jobs to be done`: `Job \| Role \| When \| I want to \| So I can \| Success number \| Requirements` | every persona in ≥ 1 role; every job has a number and cites an existing `FR-` id |
| `## Journeys and screens` | `### User journey flowchart`: Mermaid `flowchart` with start, both branches of each decision, error paths, end; `### Screens map`: `Screen \| Name \| Purpose \| Roles \| Objects \| Leads to`; `### Service blueprint`: `Step \| Screen \| Frontstage \| Backstage \| Support system \| Failure point \| Recovery \| Requirements`, steps `B-1` … | map and flowchart name the same screen ids; every role, object and `Leads to` id exists; every screen and every research support system is on a blueprint step; every failure point has a recovery; every step cites existing `FR-` ids |
| `## Objects` | index `Object \| Definition \| Owner role \| States \| Retention \| Personal data`; per object `### <Object>` with `Field \| Type \| Required \| Format \| Example` | every field has a type and an example |
| `## Capability N — <Name>` | paragraph; `Features:` (`` `slug` — text ``); `Requirements:` (`FR-N.m`: behaviour, condition, observable outcome, including what the system refuses); `Success criteria:` (`` SC-n (`feature-slug`): text ``); `Limits:`; `Screens:` ids | numbered 1..N; ≥ 3 requirements and ≥ 1 feature each; ≥ 1 success criterion per feature |
| `## <Name> policy` *(only when a model or a formula scores, grades or ranks something; a person's plain confirm or dismiss needs none)* | tiers, thresholds, a human-always class, worked examples with the arithmetic | one section per scored judgment, placed after the capability that uses it |
| `## Architecture` | table `Product component \| Pattern \| Role`; source of truth, tenancy, residency | names roles, never vendors or libraries — the stack is the TRD's decision |
| `## Non-functional requirements` | table `Area \| Requirement`; areas Security, Privacy, Performance, Availability, Accessibility, Auditability; add Cost control when the product calls a model or meters spend | every row has a number or a named standard |
| `## Metrics and success criteria` | table `Metric \| Definition \| Target`; `What is not measured:` | numeric targets |
| `## Scope, phases, and release plan` | table `Phase \| Ships \| Gate`; `Out of scope` paragraph; `Dependencies:` | numeric gates |
| `## Risks and open questions` | table `Risk \| Mitigation`; `Open questions:` each a choice with options, or `None.` | mitigation names control, detection and consequence |

**Ids are the contract.** `FR-N.m`, `SC-n`, `P-n`, screen ids (`S-01`), job ids (`JTBD-1`), blueprint steps (`B-1`), object names and feature slugs never change once approved; a retired id is struck, never reused. Feature slugs become `features/<capability-slug>/<feature-slug>.feature`.

**`Screens:` lines drive the UI stage.** Branding runs only when the PRD names screens, and it draws one screen per id on these lines. A screen missing from a `Screens:` line is a screen nobody draws; a screen several capabilities share (sign-in, settings) goes on the line of the first capability that needs it.

**Product kind.** `service`: no screens. `ui`: screens with no API or data store of its own. `ui_and_service`: screens plus its own API or data store — most web applications.

**A number nobody gave you.** Every target, gate and non-functional row needs a number, because the next reader will build to it. When the research and the brief give none, propose one, mark it `(assumed)` and add the choice to Open questions; the product owner confirms or corrects it at the checkpoint. An unmarked invented number reads as a promise; a missing one fails the lint.

## Modes

- **new**: the whole document, version `v1.0`.
- **amendment**: edit the living PRD in place, keeping every heading and id; add capabilities with the next number; bump the version (minor for a capability, patch for a corrected number). Write `docs/initiatives/<id>/impact.md` with `## Sections changed`, `## Units affected` and `## ADRs touched`. Change only what the initiative or change request cites — the `revision_scope` gate compares everything else byte for byte.
- **as-built**: describe what the product does today. Every capability cites ≥ 1 code path or route in backticks; anything inferred carries the word `inferred` and its evidence on the same line; the Principles are inferred from the code and marked `inferred`.

## Checklist the product owner signs

- Users, goals, non-goals and success metrics state the intent.
- Every success criterion will have ≥ 1 scenario (the `po-evals` skill writes them next).
- Principles hold ≤ 10 articles, each with its compliance check.
- As-built: every `inferred` item carries evidence.

## Limits

Writes only `docs/prd/**` and `docs/initiatives/**`. A fact the research does not support is marked `(assumed)` and listed as an open question, never stated as settled. Two gate corrections, then `blocked(doc_lint)` with the lint output.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
