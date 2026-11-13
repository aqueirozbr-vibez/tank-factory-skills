---
name: context-build
description: Context stage of the Tank Factory Architect (Architect hat) — compile the approved PRD, TRD and styleguide into the six context files under context/ (project-overview, architecture, ui-context, code-standards, ai-workflow-rules, progress-tracker) plus AGENTS.md and CLAUDE.md, so they pass the context gate. Use at the context stage of a brief, for a context revision or a discovery batch, or when someone asks for AGENTS.md, context files or agent-ready project documentation for a repository.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# context-build

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Architect | context build (`brief_to_backlog/*`), `context_revision`, discovery batch | `context/*.md` (exactly six), root and nested `AGENTS.md`, `CLAUDE.md` | the context gate (below) | tech lead |

Every agent reads these files before every phase, in a fixed order, and may not start if they exceed 40,000 tokens together. They are the product **distilled for a reader with no memory**: what it is, how it is shaped, what must always hold, how to work here. They are compiled from approved documents, so nothing in them is new — a fact that is not in the PRD, the TRD or the styleguide does not belong here until it is there first.

## Inputs

- The approved PRD, TRD (with its `stack_profile`) and `docs/design/styleguide.md`.
- `evals/tech/` (the checks the invariants point at) and, for brownfield, the graph report.
- Revision: the task's `context_conflict`, or the batch of discovery notes, each with its evidence.

## Steps

1. **project-overview.md** from the PRD: product, roles, features, scope, principles, glossary. Done when every PRD feature slug and every `P-n` article is listed, and the glossary holds every name the other files use.
2. **architecture.md** from the TRD: the stack table, the boundaries (TRD §4), the invariants (§4.1) with their check paths, and pointers to the TRD headings for data, interfaces and integrations. Done when no stack cell is empty, every boundary's folder exists in the repository or the build plan, and there are ≥ 4 invariants whose check files exist.
3. **ui-context.md** from the styleguide: tokens with values, fonts and icons, breakpoints, components and their states. A product with no screens writes the single line `No UI: product kind service.`
4. **code-standards.md** from the stack profile and `evals/tech/standards/`: each rule names the language, library or tool it applies to and the lint rule or Code health smell that enforces it. Done when no rule is generic — a rule nothing enforces is advice the Reviewer cannot grade.
5. **ai-workflow-rules.md**: the read order, how to work inside one boundary, the units-and-specs rule (one unit at a time, each built only from its own approved spec), the verification checklist naming the profile's real quality commands, the empty generated block for protected files, and what to do when the context falls short.
6. **progress-tracker.md**: the generated header from `assets/` and nothing else. Code renders the live tracker from the trace.
7. **AGENTS.md** at the root, listing the six files in order, and `CLAUDE.md` containing `@AGENTS.md`. Add a nested `AGENTS.md` only where a folder has rules that apply nowhere else.
8. **Self-check.** `python3 scripts/lint_context.py --root <repository root> --trd docs/trd/<product>.md [--build-plan specs/00-build-plan.md]`. Done at 0 fail.
9. **Return the envelope**: `phase: context`, one artifact of kind `context` per file. The `build-plan` skill runs next in the same stage.

## Shape

Start each file from its template in `assets/`; `references/exemplar/` holds a passing set (its entry files are named `AGENTS.example.md` and `CLAUDE.example.md` so no harness loads them as instructions). Write them in English whatever the project's language, because every agent prompt is English. Keep the six files near 25,000 tokens so nested `AGENTS.md` files and later revisions fit under the cap: point to a TRD heading instead of copying its tables.

| File | Sections | The gate checks |
| --- | --- | --- |
| `project-overview.md` | Product · Users and roles · Features (`Feature \| Capability \| Feature file`) · Scope · Principles (`Article \| Principle \| Compliance check`) · Glossary (`Name \| Kind \| Defined in`) · Documents | no scaffold text |
| `architecture.md` | Stack (`Repository \| Language \| Package manager \| Base image \| Frameworks and libraries`) · Boundaries (`Boundary \| Folder \| Responsibility \| May import \| Never imports`) · Invariants (`ID \| Invariant \| Check`) · Data · Interfaces | stack table complete; every boundary names an existing folder; ≥ 4 invariants, each mapped to ≥ 1 check in `evals/tech/` |
| `ui-context.md` | Tokens (`Token \| Value \| Use`) · Fonts and icons · Breakpoints · Components and states · Rules | every token row has a value |
| `code-standards.md` | Rules (`Rule \| Applies to \| Enforced by`) · Tests · Naming | every rule names a stack noun |
| `ai-workflow-rules.md` | Read first · How to work · Units and specs · Verification checklist · Protected files · When the context falls short · Hard limits | Units and specs names the build plan, the spec path `specs/<task>-<slug>.md`, approval before code and `spec_defect`; the protected-files block is generated, not typed; the checklist names the quality commands |
| `progress-tracker.md` | the generated header | nothing but the header |

**The protected-files block.** Leave it exactly as the template has it — an empty block between `<!-- factory:generated protected-files -->` and `<!-- /factory:generated -->`. Code fills it from the protected set; typed entries would drift from what the hooks enforce.

**Scaffold text** is anything that reads as a template: square-bracket placeholders, `e.g.`, angle-bracket fillers, `TBD`. The gate fails on each, because an agent treats a placeholder as a fact.

## Revision mode

A context revision changes only the lines its cause cites: the two contradicting lines of a `context_conflict`, or the notes of a discovery batch. If the fix belongs in the PRD or the TRD, say so in `open_questions[]` for that document's approver instead of patching the context around it — the context stays a compilation. The same lint is the gate; the tech lead approves the PR.

## Checklist the tech lead signs

- The six files and `AGENTS.md` pass the context gate.
- Every boundary and invariant in `architecture.md` matches the approved TRD.

## Limits

Writes only `context/**`, `AGENTS.md` files and `CLAUDE.md`. Never writes the live progress tracker or `.factory/`. Two gate corrections, then `blocked(context_gate)` with the failing checks.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
