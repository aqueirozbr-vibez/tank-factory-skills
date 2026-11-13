---
name: tech-lead-evals
description: Technical stage of the Tank Factory Architect (Tech Lead hat) — write the conformance checks under evals/tech/ that make the TRD enforceable, with one executable check per architecture invariant, one import contract per component boundary and the standards lint configuration. Use right after a TRD's component map and invariants are written or amended, or when someone asks for architecture tests, import-boundary rules or fitness functions for a codebase.
license: CC-BY-4.0 · © 2026 Tank Factory
---

# tech-lead-evals

| Hat | Stage | Writes | Code gate | Approver |
| --- | --- | --- | --- | --- |
| Tech Lead | technical (`brief_to_backlog/*`), revision | `evals/tech/**` | every invariant maps to ≥ 1 check; ≥ 1 import contract per boundary | tech lead, with the TRD |

These checks run in every pull request's gate ladder. They are how the TRD stops being a document and becomes a **tripwire**: a Builder that crosses a boundary or breaks an invariant is stopped by code, before any reviewer reads the diff. A check earns its place when it goes red on the violation and stays green otherwise — including on an empty repository, because it runs from the first unit on.

## Inputs

- TRD §4 Component map (folders and import rules) and §4.1 Invariants (ids, statements, check paths).
- TRD §2 `stack_profile`: `boundary_check` names the tool, `quality.test` runs the invariant checks, `quality.lint` loads the standards.
- The PRD's Principles, for the articles whose compliance check lives here.

## Steps

1. **Boundaries.** For each repository, write one import contract per component-map row in the boundary tool's own format, under `evals/tech/boundaries/`: what the folder may import and what it must never import. Done when every folder in the component map appears in a contract.
2. **Invariants.** For each `INV-n`, write the check at the path TRD §4.1 names. Open it with the header below. Done when every invariant has a file and each file would fail on the violation its header describes.
3. **Standards.** Write the lint configuration for the rules `code-standards.md` will state, under `evals/tech/standards/`, extending the stack's default. Done when each maintainability rule (one responsibility per function, nesting depth, swallowed exceptions, magic numbers, resource handling) maps to an enabled rule.
4. **Index.** Write `evals/tech/README.md` with the two tables in Shape. Done when every invariant and every component has a row.
5. **Self-check.** `python3 scripts/lint_tech_evals.py --trd docs/trd/<product>.md --root <repository root> [--root <second repository>]`. Done at 0 fail.
6. **Return** artifacts of kind `tech_evals` in the technical stage's envelope.

## Shape

`references/exemplar/` holds a passing `evals/tech/` tree.

```
evals/tech/
  README.md        index of invariants and boundaries
  boundaries/      import contracts (dependency-cruiser config, import-linter contracts)
  invariants/      one check per invariant, run by the test command
  standards/       lint configuration for the code standards
```

Every invariant check opens with this header, as a comment or docstring:

```
Invariant: INV-2 — A reading id is stored at most once; a repeat returns the first result.
Fails when: a second POST with the same id inserts a row or returns a different body.
Live from: the unit that builds app/readings/.
```

`README.md`:

| Table | Columns | Pass test |
| --- | --- | --- |
| Invariants | `ID \| Check \| Command` | one row per TRD invariant; the command runs that one check |
| Boundaries | `Component \| Folder \| Contract` | one row per component-map row |

## Writing a check that can be trusted

- **Prefer structure over behaviour.** A check that reads the source tree, the schema or the route table (an import contract, an AST scan, a migration assertion) is deterministic and holds on an empty tree. Reach for a behavioural test only when the invariant is about behaviour.
- **Green on nothing, red on the violation.** Before its module exists, a check passes because there is nothing to violate it — say so in `Live from:`. It never passes by being skipped: a skipped check is a tripwire that is switched off.
- **One invariant per file**, named `test_inv_<n>_<slug>`, so a failing gate names the invariant.
- **No network, no clock, no order dependence**, so a red result always means the code changed.
- **State the seeded violation** in `Fails when:`. It is the sentence a reviewer uses to prove the check works, and the Reviewer cites the same invariant when it rejects a diff.

## Checklist the tech lead signs

- Every invariant maps to ≥ 1 check.
- Every boundary has an import contract in the tool the stack profile names.

## Limits

Writes only `evals/tech/**`; never product code, tests under `tests/`, or CI configuration. In a product with several repositories, each repository carries the checks for its own folders under its own `evals/tech/`. Two gate corrections, then the stage blocks with the gate output.

## Outside the factory

Run by a person in Claude instead of by the factory, there is no envelope, gate or checkpoint: deliver the files and list the open questions in the reply. When `assets/`, `references/` or `scripts/` are missing because the skill was installed as a single file, build from the Shape section and walk its pass tests by hand in place of the lint.
