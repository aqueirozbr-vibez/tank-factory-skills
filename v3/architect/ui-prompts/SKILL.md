---
name: ui-prompts
description: Branding stage of the Tank Factory Architect (Designer hat) — write the UI brief docs/design/ui-prompts.md (journey maps and one screen prompt per PRD screen id, with mobile view and states) and the styleguide docs/design/styleguide.md (token table, fonts, icons, breakpoints, components and their states), then drive Figma when the project has a file. Use when a PRD names screens and the product needs journeys, a design system, key screens, a mobile layout or component states, or when someone asks for prompts for Figma Make or Claude Design.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# ui-prompts

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Designer | branding (`brief_to_backlog/*`), only when the PRD names screens | `docs/design/ui-prompts.md`, `docs/design/styleguide.md`; the project's Figma file through the sidecar | token table complete; one screen per PRD `Screens:` id | Designer, or the product owner when the project has none |

Branding fixes how every screen looks and behaves **before** anyone plans or builds it. Whatever this stage leaves undrawn — a breakpoint, an empty state, an error message — an agent will later have to ask about or guess. So the bar is **every screen, every width, every state**.

## Pick the path

| The project has… | Do | Then |
| --- | --- | --- |
| a Figma file and no frames of its own for these screens | steps 1–4, then build variables, a styleguide page and one key-screen frame per screen id through the `figma` MCP, from the bound design system | regenerate the token table from the file's variables so the styleguide matches the file |
| the team's own Figma frames or design system named as the source (design-first) | steps 1–3 against those frames; generate no screens; complete the token table from their variables | raise every PRD screen with no frame as a question to the Designer |
| no Figma file | steps 1–4 | hand over to the `wireframes` skill |
| Figma unreachable | steps 1–4, note `figma_unavailable` in the envelope | continue with `wireframes` |

## Steps

1. **Journey maps.** For each PRD persona, map their journey with the product: each step's stage, screen, action and result, how it feels (a score from -2 to +2 with a word), and for every negative step the pain point and the design response that answers it. Build the steps from the PRD's journey flowchart and service blueprint; take the pains from the research. Done when every persona has a map, every node of the PRD flowchart is a row, every screen id in the PRD's screens map appears, and every negative step has a design response.
2. **Styleguide.** Write `docs/design/styleguide.md`: tokens, fonts and icons, breakpoints, components, component states. Use the project's design system when one is bound; otherwise an open-source stack with no brand tokens unless the brief gives them. Done when no token has an empty value and every interactive component has its states.
3. **Screen prompts.** One `### <id> — <Name>` section per PRD screen id, complete enough to hand to Figma Make or Claude Design unchanged. Done when each prompt states its mobile view and its states, and every field it shows exists in the PRD's Objects.
4. **UI scenarios.** List, per screen, the `@ui` scenarios in `features/` that exercise it; add the missing ones in the `po-evals` shape. Done when every screen has ≥ 1 scenario and every `@ui` scenario names its screen.
5. **Self-check.** `python3 scripts/lint_ui.py docs/design/ui-prompts.md docs/design/styleguide.md --prd docs/prd/<product>.md`. Done at 0 fail.
6. **Return the envelope**: `phase: branding`, artifacts of kind `styleguide` and `figma` (with the file link) or `wireframes`.

Start from the two templates in `assets/`; `references/` holds a passing UI brief and styleguide.

## Shape — `docs/design/ui-prompts.md`

| Section | Contains | Pass test |
| --- | --- | --- |
| `# UI brief — <Product>` + byline | date · traces to PRD version · path (`figma`, `design-first` or `wireframes`) | present |
| `## Journey maps` | one `### <Persona> — <role>` per PRD persona, table `Step \| Stage \| Screen \| Action \| Result \| Feeling \| Pain point \| Design response \| Next` | every PRD persona has a map; every PRD screen id appears and every screen named exists; every feeling starts with a score from -2 to +2; every negative step has a pain point and a design response |
| `## Screen prompts` | one `### <id> — <Name>` per screen, each with the labelled lines below | one section per PRD screen id, none missing |
| `## UI scenarios` | table `Screen \| Scenario \| Feature file` | every screen has ≥ 1 row |

Each screen prompt carries these labelled lines, because they are what a design tool or a wireframe needs and what a reviewer checks:

- `Purpose:` one sentence, from the screens map.
- `Roles:` who sees it, and what a role without permission sees instead.
- `Shows:` objects and fields, by their PRD names, with real sample values from the PRD's examples.
- `Actions:` each action, its result, and where it leads.
- `Layout:` the desktop arrangement, top to bottom.
- `Mobile view:` what stacks, hides or moves at each breakpoint; touch targets ≥ 44 × 44 px.
- `States:` every component on the screen with the states it can be in here (`ReadingForm: default, offline-queued, error`), including empty, loading and error for anything that loads data.
- `Prompt:` the paragraph to paste into the design tool.

## Shape — `docs/design/styleguide.md`

| Section | Table | Pass test |
| --- | --- | --- |
| `## Tokens` | `Token \| Category \| Value \| Use` | categories colour, type, spacing, radius, elevation and motion each have ≥ 1 row; no empty value |
| `## Fonts and icons` | `Asset \| Family \| License` | every licence is open-source (OFL, Apache-2.0, MIT, ISC, CC0, CC-BY) |
| `## Breakpoints` | `Name \| Min width \| Layout change` | ≥ 2 rows, one at ≤ 480 px |
| `## Components` | `Component \| Use \| Interactive` | every component a screen prompt names is listed |
| `## Component states` | `Component \| State \| Appearance \| Message` | every interactive component has default, hover, focus and disabled; every `error` row has its message text |

Token names use dots (`color.primary`); the `wireframes` skill turns them into CSS variables (`--color-primary`) and the `context-build` skill copies the table into `context/ui-context.md`, so this table is the single source for values.

## Checklist the Designer signs

- One screen or wireframe per PRD `Screens:` id.
- Token table complete.
- Journey maps cover every persona and every PRD screen; every negative step has a design response.
- Every UI scenario names the screen it exercises.

## Limits

Writes only `docs/design/**`; the Figma file is written through the sidecar, which code operates. A frame the Designer edits by hand makes the Designer its author. State is never shown by colour alone. Two gate corrections, then the stage blocks with the gate output.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
