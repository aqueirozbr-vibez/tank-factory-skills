# Conformance checks — Reading Capture

Run in every pull request's gate ladder. Fictional exemplar: both repositories' checks are shown in one tree.

## Invariants

| ID | Check | Command |
| --- | --- | --- |
| INV-1 | `evals/tech/invariants/test_inv_1_no_silent_drop.py` | `pytest evals/tech/invariants/test_inv_1_no_silent_drop.py` |
| INV-2 | `evals/tech/invariants/test_inv_2_idempotent_write.py` | `pytest evals/tech/invariants/test_inv_2_idempotent_write.py` |
| INV-3 | `evals/tech/invariants/test_inv_3_registry_read_only.py` | `pytest evals/tech/invariants/test_inv_3_registry_read_only.py` |
| INV-4 | `evals/tech/invariants/test_inv_4_revision_on_correction.py` | `pytest evals/tech/invariants/test_inv_4_revision_on_correction.py` |
| INV-5 | `evals/tech/boundaries/importlinter.ini` | `lint-imports --config evals/tech/boundaries/importlinter.ini` |

## Boundaries

| Component | Folder | Contract |
| --- | --- | --- |
| capture | `src/capture/` | `evals/tech/boundaries/.dependency-cruiser.cjs` rule `capture-isolated` |
| review | `src/review/` | rule `review-isolated` |
| sync | `src/sync/` | rule `sync-isolated` |
| api-client | `src/api/` | rule `api-client-leaf` |
| ui | `src/ui/` | rule `ui-leaf` |
| readings | `app/readings/` | `evals/tech/boundaries/importlinter.ini` contract `readings-forbidden` |
| anomalies | `app/anomalies/` | contract `anomalies-forbidden` |
| assets | `app/assets/` | contract `assets-forbidden` |
| registry_client | `app/integrations/registry/` | contract `registry-read-only` |
| summaries | `app/summaries/` | contract `summaries-never-decide` |
| db | `app/db/` | contract `db-leaf` |

## Standards

`evals/tech/standards/ruff.toml` and `evals/tech/standards/eslint.config.mjs` enable the rules `context/code-standards.md` cites.
