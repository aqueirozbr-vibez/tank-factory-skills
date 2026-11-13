# Code standards — Reading Capture

Every rule names what it applies to and what enforces it. The Reviewer grades only what a rule here enforces.

## Rules

| Rule | Applies to | Enforced by |
| --- | --- | --- |
| One responsibility per function: ≤ 40 statements, ≤ 12 branches | Python | ruff `PLR0915`, `PLR0912` |
| Cyclomatic complexity ≤ 10 | Python | ruff `C901` |
| No swallowed exceptions or catch-alls | Python | ruff `BLE001`, `S110` |
| No magic numbers | Python | ruff `PLR2004` |
| Files and connections are opened with a context manager | Python | ruff `SIM115` |
| Functions are ≤ 60 lines and nesting is ≤ 3 deep | TypeScript | eslint `max-lines-per-function`, `max-depth` |
| No empty catch blocks | TypeScript | eslint `no-empty` |
| No magic numbers | TypeScript | eslint `@typescript-eslint/no-magic-numbers` |
| Every promise is awaited or handled | TypeScript | eslint `@typescript-eslint/no-floating-promises` |
| FastAPI routers hold no SQL; they call a service | FastAPI | import contracts in `evals/tech/boundaries/importlinter.ini` |
| React components style with token variables only | React | Reviewer, against `ui-context.md` Rules |
| Decimals are `Decimal` in Python and strings on the wire | Python, TypeScript | mypy strict; the types in TRD §8.1 |

## Tests

- Python: unit tests in `tests/unit/`, integration tests in `tests/integration/`, run with `pytest`.
- TypeScript: unit tests in `tests/unit/`, run with `pnpm test` (Vitest).
- A test asserts behaviour; a test with no assertion, or one that special-cases its input, is a finding.

## Naming

- Python: modules and functions in snake_case, classes in PascalCase.
- TypeScript: files in kebab-case, components and types in PascalCase.
- Use the Glossary's names in code: a synonym is a second thing.
