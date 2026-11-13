# AI workflow rules — Reading Capture

## Read first

In this order, every phase: `project-overview.md`, `architecture.md`, `ui-context.md`, `code-standards.md`, `ai-workflow-rules.md`, `progress-tracker.md`; then the `AGENTS.md` of every folder you touch; then the unit's spec.

## How to work

- The spec is the contract: build what it says, inside the boundary it names.
- Find things with the code graph before reading files.
- Use the Glossary's names. Cite PRD and TRD sections by heading.
- Write tests first where the spec gives a focused test.

## Units and specs

- Work follows `specs/00-build-plan.md`, one unit at a time. A unit starts only when every unit in its `Depends on:` line is merged.
- Every unit has its own spec, `specs/<task>-<slug>.md`, written and approved before any of the unit's code: Outcome, Scope, acceptance criteria bound to tests, and phases when the unit is large.
- The Planner writes and changes specs; every other role reads them as they are.
- No approved spec for the unit: stop before writing any code. A planning session writes the spec and waits for its approval; any other session asks for it. The build plan entry alone is never enough to build from.
- A spec that cannot be built as written: stop and report `spec_defect` with the line.

## Verification checklist

Run these before returning, per repository, and include the results:

- fieldco/reading-web: `pnpm format:check` · `pnpm lint` · `pnpm typecheck` · `pnpm test`
- fieldco/reading-api: `ruff format --check` · `ruff check` · `mypy .` · `pytest`
- Focused tests: `pnpm vitest run {files}` and `pytest {files}`

## Protected files

<!-- factory:generated protected-files -->
<!-- /factory:generated -->

## When the context falls short

- Incomplete but consistent: record a discovery note (kind, text, the context line, your evidence) and continue.
- A spec line contradicts a context line: stop and report `context_conflict` with both lines. Never edit `context/`.
- A requirement nobody stated: ask a blocking question. Never invent behaviour.

## Hard limits

No commits, pushes, installs or network calls; code performs them. A change to a dependency manifest or a protected file stops the task for a person.
