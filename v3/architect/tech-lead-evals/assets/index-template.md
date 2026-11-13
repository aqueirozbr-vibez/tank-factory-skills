# Conformance checks — <Product name>

Run in every pull request's gate ladder.

## Invariants

| ID | Check | Command |
| --- | --- | --- |
| INV-1 | `evals/tech/invariants/<file>` | `<command that runs this one check>` |

## Boundaries

| Component | Folder | Contract |
| --- | --- | --- |
| <component> | `<folder/>` | `evals/tech/boundaries/<file>` rule or contract `<name>` |

## Standards

`evals/tech/standards/<file>` enables the rules `context/code-standards.md` cites.
