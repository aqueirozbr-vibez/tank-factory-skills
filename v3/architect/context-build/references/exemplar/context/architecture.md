# Architecture — Reading Capture

Compiled from `docs/trd/reading-capture.md` v1.0. Cite TRD sections by heading for detail.

## Stack

| Repository | Language | Package manager | Base image | Frameworks and libraries |
| --- | --- | --- | --- | --- |
| fieldco/reading-web | TypeScript 5.6 | pnpm 9 | registry.example/approved/node:22-bookworm | React, a service worker with IndexedDB, Vitest, Playwright |
| fieldco/reading-api | Python 3.12 | uv 0.4 | registry.example/approved/python:3.12-slim | FastAPI, PostgreSQL 16, pytest, ruff, mypy |

## Boundaries

One boundary per unit of work. A change that needs two boundaries is two units.

| Boundary | Folder | Responsibility | May import | Never imports |
| --- | --- | --- | --- | --- |
| capture | `src/capture/` | S-01 screen and ReadingForm | `src/sync/`, `src/api/`, `src/ui/` | `src/review/` |
| review | `src/review/` | S-02 screen, AnomalyTable, DecisionButtons | `src/api/`, `src/ui/` | `src/capture/`, `src/sync/` |
| sync | `src/sync/` | Local queue; sends each reading once | `src/api/` | `src/capture/`, `src/review/` |
| api-client | `src/api/` | Typed client for the endpoint map | nothing in `src/` | `src/capture/`, `src/review/`, `src/sync/` |
| ui | `src/ui/` | Token variables and shared controls | nothing in `src/` | `src/capture/`, `src/review/`, `src/sync/`, `src/api/` |
| readings | `app/readings/` | Idempotent write; corrections with revisions | `app/assets/`, `app/db/` | `app/anomalies/`, `app/summaries/`, `app/integrations/` |
| anomalies | `app/anomalies/` | Range check, queue, decisions | `app/readings/`, `app/assets/`, `app/summaries/`, `app/db/` | `app/integrations/` |
| assets | `app/assets/` | Asset mirror | `app/integrations/registry/`, `app/db/` | `app/readings/`, `app/anomalies/` |
| registry_client | `app/integrations/registry/` | The only caller of the Asset Registry; GET only | nothing in `app/` | everything else in `app/` |
| summaries | `app/summaries/` | Prompt, model call, validation | `app/db/` | `app/anomalies/`, `app/readings/` |
| db | `app/db/` | Migrations, sessions, the job queue | nothing in `app/` | everything else in `app/` |

## Invariants

These hold on every commit. Each has a check that fails when it is broken.

| ID | Invariant | Check |
| --- | --- | --- |
| INV-1 | Every reading the API acknowledges with 2xx has a row in `reading` | `evals/tech/invariants/test_inv_1_no_silent_drop.py` |
| INV-2 | A reading id is stored at most once; a repeat returns the first result | `evals/tech/invariants/test_inv_2_idempotent_write.py` |
| INV-3 | Only `app/integrations/registry/` calls the Asset Registry, and only with GET | `evals/tech/invariants/test_inv_3_registry_read_only.py` |
| INV-4 | Every change to `reading.value` writes a `reading_revision` row with the old value and the actor | `evals/tech/invariants/test_inv_4_revision_on_correction.py` |
| INV-5 | `app/summaries/` never imports decision code | `evals/tech/boundaries/importlinter.ini` |

## Data

- asset: mirror of the Asset Registry, refreshed every 15 min — TRD §6. Data model (MER)
- reading, reading_revision: readings and their corrections, kept 5 years — TRD §6. Data model (MER)
- anomaly: one per out-of-range reading, with a summary and a decision — TRD §6. Data model (MER)
- Decimals travel as strings so no client rounds a reading — TRD §8. Endpoint map

## Interfaces

- Endpoints: `/v1/readings`, `/v1/assets`, `/v1/anomalies` — TRD §8. Endpoint map
- Integrations: Asset Registry (GET only, 5 s timeout), model provider (10 s timeout) — TRD §9. Integration sequences
- Model calls: anomaly_summary, which writes one sentence and decides nothing — TRD §10. AI orchestration and protocols
