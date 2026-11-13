---
name: wireframes
description: Branding stage of the Tank Factory Architect (Designer hat) — draw one static HTML wireframe per PRD screen id under docs/design/wireframes/, with styleguide tokens as CSS variables, a mobile layout, every component state and no external network reference. Use when a product with screens has no Figma file or Figma is unreachable, or when someone asks for HTML wireframes or mockups of a product's key screens, mobile view or component states.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# wireframes

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Designer | branding (`brief_to_backlog/*`), when the project has no Figma file | `docs/design/wireframes/<id>-<name>.html` | one wireframe per PRD `Screens:` id; valid HTML; no external network references; tokens as CSS variables | Designer, or the product owner when the project has none |

A wireframe is the screen's **specification you can open**: the Designer approves it, the Planner writes specs against it and the Builder builds from it. It shows structure, content and states, at phone and desktop width. It is one self-contained file because agents and reviewers open it offline, inside a sandbox with no network.

## Inputs

- `docs/design/ui-prompts.md` (the screen prompt per id) and `docs/design/styleguide.md` (tokens, breakpoints, components and states) from the `ui-prompts` skill.
- The PRD's screens map and object examples.

## Steps

1. **One file per screen id** on the PRD's `Screens:` lines, named `<id>-<name-slug>.html` in lowercase (`s-01-reading-capture.html`), starting from `assets/wireframe-template.html`. Done when the folder holds exactly one file per id.
2. **Copy the tokens.** Every styleguide token becomes a CSS variable in `:root`, dots to dashes (`color.primary` → `--color-primary`). Style only with `var(--…)`, so a token change is a one-line change. Done when every token is declared and every `var()` used is declared.
3. **Draw the screen** from its prompt: the `Layout:` at desktop width, the `Mobile view:` at the phone breakpoint, phone first. Fill it with the PRD's example values, never filler text. Done when each `Shows:` field and each `Actions:` control is on the page.
4. **Draw the states.** Under the main view, a `<section class="states">` renders each component in each state the prompt's `States:` line lists, every one marked `data-component="<Name>" data-state="<state>"`, with the styleguide's exact message text. Done when no listed state is missing.
5. **Self-check.** `python3 scripts/lint_wireframes.py docs/design/wireframes --prd docs/prd/<product>.md --styleguide docs/design/styleguide.md --ui-prompts docs/design/ui-prompts.md`. Done at 0 fail.
6. **Return the envelope**: `phase: branding`, one artifact of kind `wireframes` per file.

## Shape of a wireframe

`references/exemplar/` holds two passing wireframes.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>S-01 Reading Capture</title>
  <style>
    :root { --color-ink: #17202a; --space-4: 16px; /* every styleguide token */ }
    /* phone first; then */
    @media (min-width: 1024px) { /* desktop layout */ }
  </style>
</head>
<body data-screen="S-01">
  <main> <!-- the screen in its default state, with real values --> </main>
  <section class="states"> <!-- one block per component × state --> </section>
</body>
</html>
```

- **Self-contained.** One `<style>` block; no `<script>`; no `http://` or `https://` in any `src`, `href`, `url()` or `@import`. Fonts are named with a system fallback (`Inter, system-ui, sans-serif`) and never fetched. Icons are inline SVG or text.
- **Links between screens** are relative file names (`href="s-02-review-queue.html"`), following the screens map's `Leads to`.
- **State without colour.** Every state carries a word or an icon as well as its colour; the focus state is visible on a keyboard.
- **Accessible structure.** One `<h1>`, labelled inputs, buttons that are `<button>`, tables with `<th>`.

## Checklist the Designer signs

- One wireframe per PRD `Screens:` id.
- Tokens as CSS variables, table complete.
- Wireframes carry no external network reference.

## Limits

Writes only `docs/design/wireframes/**`. A wireframe fixes structure, content and states; pixel-level polish belongs to the design tool. Two gate corrections, then the stage blocks with the gate output.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
