# Tank Factory — Architect skills, new-product path

Nov 11, 2026 · batch 1 of 2 · traces to PRD — Tank Factory v3 (v6.2), §A3 Architect and §A12.6 `brief_to_backlog`

© 2026 Tank Factory · CC BY 4.0 · see [NOTICE.md](NOTICE.md)

Ten skills the Architect agent loads to turn a brief into a backlog. Each skill is one stage's instructions, its template, a passing exemplar and a lint script that mirrors the stage's code gate. The 28 building blocks of the Initial Context are required sections, checked by the lints.

## Skills

| Hat | Skill folder | Factory id | Stage | Writes | Lint |
| --- | --- | --- | --- | --- | --- |
| Product Owner | `architect/product-research` | `product_research` | discovery | `docs/research/<brief>.md` | `lint_research.py` |
| Product Owner | `architect/prd` | `prd` | product | `docs/prd/<product>.md`, `docs/initiatives/<id>/impact.md` | `lint_prd.py` |
| Product Owner | `architect/po-evals` | `po_evals` | product | `features/**`, holdout bindings | `lint_features.py` |
| Designer | `architect/ui-prompts` | `ui_prompts` | branding | `docs/design/ui-prompts.md`, `docs/design/styleguide.md`, Figma | `lint_ui.py` |
| Designer | `architect/wireframes` | `wireframes` | branding | `docs/design/wireframes/*.html` | `lint_wireframes.py` |
| Tech Lead | `architect/trd` | `trd` | technical | `docs/trd/<product>.md` | `lint_trd.py` |
| Tech Lead | `architect/stack-profile` | `stack_profile` | technical | the profile block in TRD §2 and the envelope | `lint_stack_profile.py` |
| Tech Lead | `architect/tech-lead-evals` | `tech_lead_evals` | technical | `evals/tech/**` | `lint_tech_evals.py` |
| Architect | `architect/context-build` | `context_build` | context build | `context/*.md`, `AGENTS.md`, `CLAUDE.md` | `lint_context.py` |
| Architect | `architect/build-plan` | `build_plan` | context build | `specs/00-build-plan.md`, `units[]` | `lint_build_plan.py` |

Each folder holds `SKILL.md`, `assets/` (templates), `references/` (a passing exemplar) and `scripts/` (the lint and its helper `_md.py`, standard library only).

## The 28 building blocks

| Essential | Block | Skill | Lives in | Checked by |
| --- | --- | --- | --- | --- |
| Discovery | Personas | product-research | research `## Personas` | every row sourced |
| Discovery | User Journey | product-research | research `## User journey (today)` | steps `J-n`, each naming a persona |
| Discovery | Customer Blueprint | product-research | research `## Customer blueprint` | support systems named; each needs a TRD integration |
| Discovery | Competitors and References | product-research | research `## Competitors and references` | URL and verdict per row |
| PRD | User Roles | prd | PRD `### User roles` | every persona in a role |
| PRD | Jobs to be done | prd | PRD `### Jobs to be done` | a number and an `FR-` id per job |
| PRD | User Journey Flowchart | prd | PRD `### User journey flowchart` | Mermaid; every screen id on it |
| PRD | Screens Map | prd | PRD `### Screens map` and `Screens:` lines | map, flowchart and `Screens:` lines agree |
| PRD | Service Blueprint | prd | PRD `### Service blueprint` | every screen and every research support system on a step; a recovery per failure point; `FR-` ids per step |
| PRD | Objects definitions and metadata | prd | PRD `## Objects` | type and example per field |
| PRD | Functional Requirements | prd, po-evals | PRD `## Capability N` (`FR-N.m`, `SC-n`); `features/` | ≥ 3 per capability; a scenario per `SC-n` |
| PRD | Non-functional requirements | prd | PRD `## Non-functional requirements` | a number or standard per row |
| UI | Journey Maps | ui-prompts | UI brief `## Journey maps` | a map per persona; every screen on a step; a -2…+2 feeling per step; a design response per negative step |
| UI | Design System | ui-prompts | styleguide `## Tokens`, `## Fonts and icons`, `## Components` | six token categories, no empty value, open licences |
| UI | Key Features Screens | ui-prompts, wireframes | one prompt and one wireframe (or Figma frame) per screen id | exactly one per id |
| UI | Mobile View | ui-prompts, wireframes | `Mobile view:` per prompt; `## Breakpoints`; `@media` | a breakpoint ≤ 480 px; viewport meta; `@media` |
| UI | Components States | ui-prompts, wireframes | styleguide `## Component states`; `data-state` blocks | base states per interactive component; error messages drawn |
| TRD | DevOps | trd | TRD `## 12. DevOps` | rollback time; an alert per SLO |
| TRD | C4 Diagram | trd | TRD `## 3. C4 diagrams` | C4Context, C4Container, components; PRD personas present |
| TRD | Stack | trd, stack-profile | TRD `## 2. Stack` | the `stack_profile` gate |
| TRD | Network Topology | trd | TRD `## 5. Network topology` | port and auth per conduit |
| TRD | Endpoint Map | trd | TRD `## 8. Endpoint map` | every endpoint typed against §8.1 |
| TRD | Component Map | trd, tech-lead-evals | TRD `## 4. Component map`; `evals/tech/boundaries/` | a folder per component; a contract per folder; ≥ 4 invariants with checks |
| TRD | Integrations Sequence Diagrams | trd | TRD `## 9. Integration sequences` | one diagram per integration, each with `alt` and a timeout |
| TRD | MER | trd | TRD `## 6. Data model (MER)` | `erDiagram`; an entity per PRD object |
| TRD | Data Flow | trd | TRD `## 7. Data flow` | a deletion path for personal data |
| TRD | AI Orchestration & Protocols | trd | TRD `## 10. AI orchestration and protocols` | output schema and cap per call, or `None:` |
| TRD | MLOps | trd | TRD `## 11. MLOps` | an eval row with a numeric gate per call |

## Visuals

- `visuals/examples/`: 30 high-resolution boards, one per building block of the sample product plus an overview and the fourteen-link check, rendered from `examples/reading-capture/` by `visuals/build_examples.py`.
- `visuals/deck/`: the 23 slides of the deck *The Initial Context*, at 3840 × 2160.
- Index: [visuals/README.md](visuals/README.md).

## Using it

- Mount `architect/<skill>/` read-only at `/factory/skills/architect/<skill>/`. The lint file names match the Architect's Bash allow-list (`python3 /factory/skills/**/lint_*.py`).
- `python3 build.py` copies the shared helper and the exemplars into each skill and writes `skills.lock.example` (one content hash per skill).
- `python3 selftest.py` runs every lint on the exemplar product (must pass) and on a seeded violation (must fail): 29 cases.
- `examples/reading-capture/` is a small fictional product carried through all ten skills. Its `AGENTS.md` and `CLAUDE.md` are sample outputs; keep the folder out of any agent's working tree.

## Decisions made where v3 is silent

Each is a choice this package makes; confirm or change them when the v3 TRD is written.

1. **Skill names use hyphens.** v3 names skills in snake_case (`product_research`); the Agent Skills format allows only lowercase letters, digits and hyphens and requires the folder to match. The folders use hyphens and the table above maps them to the factory ids.
2. **The lints are the gates' reference implementation.** v3 names the gates (PRD lint, TRD lint, context gate, `stack_profile` gate) without specifying them. Code should run these scripts, or an equivalent, so the agent's self-check and the gate cannot disagree.
3. **The PRD shape gains three sections** — `Principles` (v3 requires it), `Journeys and screens` (flowchart, screens map and service blueprint) and `Objects` — and stable ids (`FR-N.m`, `SC-n`, `JTBD-n`, `P-n`, `S-nn`, `B-n`). The UI brief's journeys are journey maps, one per persona.
4. **The TRD has fifteen numbered sections**, one per TRD building block plus purpose, security, testing and open decisions.
5. **Bindings before a stack exists.** v3 writes bindings in the product stage, but a new product has no stack profile or repository until after the TRD checkpoint. `po-evals` writes the feature files, reports `bindings_deferred`, and writes bindings once `.factory/stack.yaml` exists. The loop needs a step for this.
6. **"One wireframe per PRD `Screens:` line"** is read as one per screen id on those lines.
7. **Research claims that rest only on the brief** are cited `brief:<field>` and pass with a warning; the v3 gate text accepts only a URL or a repository path.
8. **Generated blocks** use the markers `<!-- factory:generated protected-files -->` and `<!-- factory:generated progress-tracker … -->`; v3 says the content is generated but names no marker.
9. **Supported stacks** (`stack-profile/references/supported-stacks.json`) come from the PRD's `stack.yaml` example; the factory image's list should replace it.
10. **Token count** is estimated as characters ÷ 4 against the 40,000 cap.
11. **Several repositories.** Each repository carries its own `evals/tech/`; v3 does not yet say which repository holds `docs/`, `context/` and `specs/` for a multi-repository product.

## Not in this batch

The other ten Architect skills: `assess_intake`, `assess_research`, `assess_define`, `assess_shape`, `assess_decide`, `release_notes`, `adopt_survey`, `characterization`, `revise_requirements`, `drift_report`. The `prd`, `trd` and `context-build` skills already describe their as-built, amendment and revision modes.

## Credits

All skills and other contents of this pack are the property of Tank Factory, © 2026, licensed under CC BY 4.0. Reuse them with credit as set out in [NOTICE.md](NOTICE.md).
