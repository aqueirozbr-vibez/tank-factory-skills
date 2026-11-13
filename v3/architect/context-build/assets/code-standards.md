# Code standards — <Product name>

Every rule names what it applies to and what enforces it. The Reviewer grades only what a rule here enforces.

## Rules

| Rule | Applies to | Enforced by |
| --- | --- | --- |
| One responsibility per function: ≤ <n> statements | <language> | <lint rule> |
| Nesting depth ≤ <n> | <language> | <lint rule> |
| No swallowed exceptions or catch-alls | <language> | <lint rule> |
| No magic numbers | <language> | <lint rule> |
| Resources are closed by a context manager or equivalent | <language> | <lint rule> |
| <stack-specific rule> | <library or tool> | <lint rule, conformance check or Code health smell> |

## Tests

- <language>: unit tests in `tests/unit/`, integration tests in `tests/integration/`, run with `<test command>`.
- A test asserts behaviour; a test with no assertion, or one that special-cases its input, is a finding.

## Naming

- <language>: <files, functions, types>.
- Use the Glossary's names in code: a synonym is a second thing.
