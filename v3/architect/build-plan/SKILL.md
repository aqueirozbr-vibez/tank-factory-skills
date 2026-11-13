---
name: build-plan
description: Context stage of the Tank Factory Architect (Architect hat) — cut the approved PRD and TRD into specs/00-build-plan.md, a dependency-ordered list of units (one boundary and one verifiable result each) grouped into build phases, with the packages each phase needs, and emit the units for the backlog. Use after the context files are built, for a build-plan delta on an initiative or change request, or when someone asks to break a product spec into a buildable, ordered backlog.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# build-plan

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Architect | context build (`brief_to_backlog/*`), revision | `specs/00-build-plan.md` and `units[]` in the envelope | acyclic; one boundary per unit; units per brief within the project setting (default 60); a build phase per unit | tech lead, after the Critic (Spec) scores the plan |

The plan is where documents become work. Code turns each unit into one tracker item with its scenarios as acceptance criteria; the Planner then writes one spec per unit, reading only that unit's entry and the PRD and TRD sections it cites. So a unit must be **buildable alone**: one boundary, one result someone can verify, and everything it needs already merged by an earlier unit.

## Inputs

- The approved PRD (requirements `FR-`, success criteria `SC-`, phases) and TRD (component map, endpoint map, MER, integrations).
- The feature files (which scenario belongs to which unit) and the context files just built.
- Delta: the existing plan, the impact report, and which units are merged, building or open.

## Steps

1. **Set the build phases** from the PRD's phases. Phase 1 is a walking skeleton: the thinnest path through every container that proves they connect. Each phase ends in something a person can see working; the Architect reports drift after each. Done when every phase has a goal and an exit check with a number or a named scenario.
2. **Cut the units.** Walk each phase's requirements and cut along the TRD's component folders: one boundary per unit. Where a feature crosses boundaries, cut the contract first (types, schema, client), then each side. Size each unit so one spec covers it without phases: about ≤ 400 changed lines and ≤ 10 files. Done when every `FR-` id is cited by ≥ 1 unit.
3. **Order them.** A unit depends only on lower-numbered units. Done when every dependency points backwards and no unit's phase is earlier than a phase it depends on.
4. **Give each unit its proof**: the verifiable result in one sentence, and a verify list of checks a person or a test can run. Attach each non-manual scenario to the unit whose merge makes it pass. Done when every `SC-` id is attached to a unit.
5. **List the packages** each unit needs as `name@version`, and collect them per build phase. Agents never install anything: code opens one dependency PR per phase from this list.
6. **Self-check.** `python3 scripts/lint_build_plan.py specs/00-build-plan.md --prd docs/prd/<product>.md --trd docs/trd/<product>.md [--max-units 60]`. Done at 0 fail.
7. **Emit the units.** `python3 scripts/lint_build_plan.py specs/00-build-plan.md --emit-units` prints the envelope's `units[]`; copy it unchanged, so the tracker items match the document.

More than the unit limit means the brief is too large for one plan: set `status: needs_human` and say where to split it.

## Shape

Start from `assets/build-plan-template.md`; `references/exemplar.md` is a passing plan.

| Section | Contains | Pass test |
| --- | --- | --- |
| `# Build plan — <Product>` + byline | date · mode (`new` or `delta`) · traces to PRD and TRD versions | present |
| `## Build phases` | table `Phase \| Goal \| Units \| Exit check` | every unit belongs to exactly one phase |
| `## Units` | one `### Unit <n> — <Name>` per unit, numbered from 1 with no gaps, each with the lines below | all lines present |
| `## Dependencies per build phase` | table `Phase \| Repository \| Package \| Needed by` | every package a unit lists appears under its phase |

Each unit carries these labelled lines:

- `Goal:` what exists after this unit that did not before, in one sentence.
- `Repository:` `owner/name`.
- `Boundary:` exactly one folder from the TRD's component map, in backticks.
- `Build phase:` a number.
- `Depends on:` earlier unit numbers, or `none`.
- `Dependencies:` packages as `name@version`, or `none`.
- `Cites:` the PRD and TRD headings the Planner must read, with the `FR-` ids: `PRD §Capability 1 — Reading capture (FR-1.1, FR-1.3); TRD §8. Endpoint map`.
- `Scenarios:` feature file and tags (`features/reading-capture/offline-queue.feature @SC-1`), or `none: <why this unit has no scenario of its own>`.
- `Verifiable result:` one observable sentence.
- `Verify:` a checklist of ≥ 1 item, each a command, a scenario or an observation.

## What makes a good cut

- **Vertical before complete.** Reach end to end early with a narrow slice, then widen; a plan that builds a whole layer first proves nothing until the last unit.
- **Contracts first.** The unit that defines a type, a table or a client lands before the units that use it, so both sides build against something merged.
- **No unit without a proof.** If the verifiable result is "the code exists", merge it into the unit that uses it.
- **Scenarios pull, units deliver.** Start from each scenario and ask which unit makes it pass; a scenario no unit claims is a missing unit.
- **Unknowns are questions.** A unit that depends on an open decision cites the TRD §15 row it assumes.

## Delta mode

For an initiative or a change request, append units after the highest existing number and leave merged units untouched. A changed open unit is rewritten in place; a cancelled one stays with `Goal: cancelled — <reason>` so numbering never shifts. The byline says `mode delta` and cites the impact report.

## Checklist the tech lead signs

- Build plan acyclic, one boundary per unit, units per brief within the project setting.
- Every requirement and every success criterion is carried by a unit.

## Limits

Writes only `specs/00-build-plan.md`. Never creates tracker items, installs a package or grants readiness: code emits the backlog as Draft and a person readies each unit or phase. Two gate corrections, then the stage blocks; a dependency cycle blocks naming the cycle.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
