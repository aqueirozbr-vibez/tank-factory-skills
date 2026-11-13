---
name: po-evals
description: Product stage of the Tank Factory Architect (Product Owner hat) — write the Gherkin feature files under features/<capability>/<feature>.feature, one per PRD feature with a scenario for every success criterion, and their hidden bindings in the holdout checkout. Use right after the PRD is drafted or amended, when success criteria need acceptance scenarios, or when someone asks for BDD scenarios, acceptance tests or product-owner evals for a product.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# po-evals

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Product Owner (UI scenarios: Designer) | product (`brief_to_backlog/*`), revision | `features/<capability>/<feature>.feature`; bindings in the holdout checkout under `tests/acceptance/features/**` | every success criterion has ≥ 1 scenario; Gherkin parses; every non-manual scenario bound; bindings fail on `main` | product owner with the PRD; the Designer for scenarios tagged `@ui` |

Feature files are the product's acceptance contract in words anyone can read: testers walk them by hand, the release runs them on staging, and the Planner extends them per unit. Bindings are how code checks them, hidden from the Builder so the build cannot be shaped to pass them. A scenario earns its place by being **falsifiable**: it fails on `main` today and passes only when the product does what the PRD says.

## Inputs

- The PRD: its `Features:` slugs, its success criteria (`` SC-n (`feature-slug`) ``), requirements, screens and objects. Use its names verbatim.
- `.factory/stack.yaml` when it exists: `bindings` names the framework (`playwright`, `pytest-bdd`).
- Amendment: the existing feature files and bindings.

## Steps

1. **Lay out the files.** One file per PRD feature slug at `features/<capability-slug>/<feature-slug>.feature`, where the capability slug is the capability's name in lowercase with dashes. Done when every slug under every `Features:` list has a file and no file lacks a slug.
2. **Write the scenarios.** For each success criterion, ≥ 1 scenario tagged `@SC-n`, in the file of the feature the criterion names. Cover the criterion's edges with further scenarios under the same tag. A refusal or failure the requirements name but no criterion covers means the PRD is missing a criterion: add it to the PRD (same stage, same hat) and tag the scenario with it, so no tag is borrowed. Done when every `SC-n` in the PRD is a tag in its own feature's file.
3. **Tag each scenario** (see Tags). Done when every scenario carries `@SC-n`, every human-judged one `@manual`, and every `@ui` one its `@screen-<id>`. Keep `@manual` for what only a person can judge; a behaviour a test can observe gets a binding.
4. **Write the bindings**, one binding file per feature file at the mirrored path `tests/acceptance/features/<capability-slug>/<feature-slug>.<ext>`, one test per non-manual scenario, titled `@SC-n <Scenario name>`. Bind through the product's public interface only: the screens for `@ui` scenarios, its API or service interface otherwise (a `ui` product with no API binds everything through its screens). Done when every non-manual scenario has its test.
5. **Self-check.** `python3 scripts/lint_features.py features --prd docs/prd/<product>.md [--bindings <holdout>/tests/acceptance/features]`. Done at 0 fail.
6. **Return the envelope**: artifacts of kind `po_evals`, one per file. The lint script is in this skill's folder; the paths it takes are relative to the repository root.

**No stack yet?** A new product has no `.factory/stack.yaml` until its TRD checkpoint, so no binding framework exists. Write the feature files, run the lint without `--bindings`, and list every non-manual scenario under `bindings_deferred` in the envelope's `evidence` (outside the factory, say so in the reply). Write the bindings in the first later stage where the stack profile exists.

## Shape of a feature file

Start from `assets/feature-template.feature`; `references/exemplar/` holds passing feature files with their bindings.

```gherkin
@capability-reading-capture
Feature: Offline queue
  Readings saved without a connection reach the server exactly once.

  Background:
    Given an inspector signed in on a phone
    And the asset "PMP-0412" is on today's route

  @SC-1
  Scenario: A reading saved offline syncs once
    Given the phone has no connection
    When the inspector saves the reading 7.25 for "PMP-0412"
    And the connection returns
    Then the server holds exactly 1 reading for "PMP-0412" with the value 7.25

  @SC-2 @ui @screen-S-01
  Scenario: Recording a reading takes at most 3 taps
    ...
```

- One `Feature:` per file, named as its slug in words (`offline-queue` → `Offline queue`), tagged `@capability-<capability-slug>`; a one-line description under it.
- Each scenario: `Given` (state), `When` (the action under test; an `And` may add the event that completes it), `Then` (an observable result), in that order. Use concrete values: start from the PRD's object examples and, when a scenario needs more, invent further values in the same format.
- Steps speak the product's language — roles, objects, screen names. Selectors, URLs and table names belong in bindings, because the feature file must stay true when the implementation changes.
- `Scenario Outline:` with `Examples:` when the same rule holds for several values.

## Tags

| Tag | Put it on | Effect |
| --- | --- | --- |
| `@capability-<slug>` | the `Feature:` line | groups the file under its capability; must match the folder |
| `@SC-n` | every scenario this skill writes (`@AC-n @task-<key>` scenarios are the Planner's, added later per unit) | links the scenario to a success criterion of its own feature; a scenario with neither tag fails the lint |
| `@manual` | a check only a person can judge: look, copy, usability | no binding; goes into the release's manual test pack |
| `@ui` + `@screen-<id>` | a scenario exercised through a screen | bound through the UI; approved by the Designer; the id must be in the PRD's screens map |
| `@smoke` | the few scenarios that prove a release is alive | run after a production deploy; the whole set must finish in ≤ 10 min |

## Bindings

- The test title carries the scenario's tag and name, so results join to success criteria: `test('@SC-1 A reading saved offline syncs once', …)` or `@scenario('offline-queue.feature', 'A reading saved offline syncs once')  # @SC-1` (pytest-bdd turns the scenario's tags into markers).
- A binding imports nothing from the product's source tree. It drives the running product, which is what makes it a judge from outside.
- A binding must fail on `main` before its unit is built. One that passes today tests nothing; tighten its `Then`.

## Checklist the approver signs

- Every success criterion has ≥ 1 scenario (product owner).
- Every UI scenario names the screen it exercises (Designer).

## Limits

Writes only `features/**` and the holdout's `tests/acceptance/features/**`. Scenario text, tags and step names are in the project's artifact language; tag ids stay stable across renames. Two gate corrections, then the stage blocks with the gate output.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
