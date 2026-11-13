# Build plan — Reading Capture

Nov 11, 2026 · mode new · traces to PRD v1.0 and TRD v1.0

Fictional exemplar.

## Build phases

| Phase | Goal | Units | Exit check |
| --- | --- | --- | --- |
| 1 | An inspector records a reading on a phone, offline or online, and it reaches the server once | 1–8 | Scenarios @SC-1, @SC-2 and @SC-3 pass on staging |
| 2 | A planner sees every out-of-range reading with a summary and decides it | 9–13 | Scenarios @SC-4 to @SC-7 pass on staging |

## Units

### Unit 1 — Schema for assets and readings

- Goal: The database has `asset`, `reading` and `reading_revision` with their keys and indexes.
- Repository: fieldco/reading-api
- Boundary: `app/db/`
- Build phase: 1
- Depends on: none
- Dependencies: `psycopg@3.2.3`
- Cites: PRD §Objects; TRD §6. Data model (MER)
- Scenarios: none: enabling unit; its proof is the migration and INV-2
- Verifiable result: The first migration applies on an empty database and `reading.id` is the primary key.
- Verify:
  - [ ] `pytest evals/tech/invariants/test_inv_2_idempotent_write.py` is green and no longer vacuous
  - [ ] The migration applies and rolls back on an empty database

### Unit 2 — Registry client

- Goal: One GET-only client reads assets from the Asset Registry with a 5 s timeout and 3 retries.
- Repository: fieldco/reading-api
- Boundary: `app/integrations/registry/`
- Build phase: 1
- Depends on: none
- Dependencies: `httpx@0.27.2`
- Cites: PRD §Capability 1 — Reading capture (FR-1.4); TRD §9. Integration sequences
- Scenarios: none: no user-visible behaviour until the mirror exists (unit 3)
- Verifiable result: Against a stubbed registry, the client returns assets, retries 3 times on 5xx and never sends a write.
- Verify:
  - [ ] `pytest evals/tech/invariants/test_inv_3_registry_read_only.py`
  - [ ] Integration test with a stub: 200, timeout, and 5xx after 3 retries

### Unit 3 — Asset mirror and asset list

- Goal: Assets are mirrored every 15 min and served by `GET /v1/assets`.
- Repository: fieldco/reading-api
- Boundary: `app/assets/`
- Build phase: 1
- Depends on: 1, 2
- Dependencies: `fastapi@0.115.0`
- Cites: PRD §Capability 1 — Reading capture (FR-1.4); TRD §8. Endpoint map
- Scenarios: none: read by the scenarios of units 4 and 8
- Verifiable result: `GET /v1/assets` returns `AssetList` with `mirrored_at`, and a failed refresh keeps the previous mirror.
- Verify:
  - [ ] Integration test: refresh, failed refresh, list
  - [ ] `lint-imports --config evals/tech/boundaries/importlinter.ini`

### Unit 4 — Idempotent reading write

- Goal: `POST /v1/readings` stores each reading id once, refuses unknown tags, and `GET /v1/readings` lists them by role.
- Repository: fieldco/reading-api
- Boundary: `app/readings/`
- Build phase: 1
- Depends on: 1, 3
- Dependencies: none
- Cites: PRD §Capability 1 — Reading capture (FR-1.1, FR-1.3, FR-1.4, FR-1.5); TRD §8. Endpoint map
- Scenarios: `features/reading-capture/offline-queue.feature` @SC-1 (The same reading sent twice is stored once)
- Verifiable result: The same `ReadingIn` posted twice yields one row and two identical answers; an unknown tag yields 422 `tag_not_found`.
- Verify:
  - [ ] The bound scenario passes
  - [ ] `pytest evals/tech/invariants/test_inv_1_no_silent_drop.py`

### Unit 5 — Typed API client

- Goal: The web client has one typed client for the endpoint map.
- Repository: fieldco/reading-web
- Boundary: `src/api/`
- Build phase: 1
- Depends on: none
- Dependencies: `vitest@2.1.4`
- Cites: PRD §Capability 1 — Reading capture (FR-1.1); TRD §8. Endpoint map
- Scenarios: none: contract unit; the types are exercised by units 7 and 8
- Verifiable result: The types in `src/api/` equal TRD §8.1 and `pnpm typecheck` passes.
- Verify:
  - [ ] `pnpm typecheck`
  - [ ] Unit tests for request building and error mapping

### Unit 6 — Token variables and shared controls

- Goal: The styleguide tokens exist as CSS variables with the shared input and button controls.
- Repository: fieldco/reading-web
- Boundary: `src/ui/`
- Build phase: 1
- Depends on: none
- Dependencies: `react@18.3.1`
- Cites: PRD §Non-functional requirements; TRD §4. Component map
- Scenarios: none: enabling unit; its states are judged on S-01 in unit 8
- Verifiable result: Every token in `context/ui-context.md` is a CSS variable, and the controls render default, hover, focus and disabled.
- Verify:
  - [ ] A unit test compares the variable list with the token table
  - [ ] Targets are ≥ 44 × 44 px at 360 px

### Unit 7 — Sync queue

- Goal: Readings are stored in IndexedDB first and sent once when a connection exists.
- Repository: fieldco/reading-web
- Boundary: `src/sync/`
- Build phase: 1
- Depends on: 4, 5
- Dependencies: `idb@8.0.2`
- Cites: PRD §Capability 1 — Reading capture (FR-1.2); TRD §7. Data flow
- Scenarios: `features/reading-capture/offline-queue.feature` @SC-1 (A reading saved offline syncs once)
- Verifiable result: A reading queued offline reaches the server exactly once within 60 s of the connection returning.
- Verify:
  - [ ] The bound scenario passes
  - [ ] `pnpm depcruise --config evals/tech/boundaries/.dependency-cruiser.cjs src`

### Unit 8 — Reading Capture screen

- Goal: S-01 lets an inspector enter a tag and a value, save, and see today's list with synced and unsent readings.
- Repository: fieldco/reading-web
- Boundary: `src/capture/`
- Build phase: 1
- Depends on: 5, 6, 7
- Dependencies: none
- Cites: PRD §Capability 1 — Reading capture (FR-1.1, FR-1.4); TRD §4. Component map
- Scenarios: `features/reading-capture/capture-reading.feature` @SC-2 @SC-3
- Verifiable result: S-01 matches `docs/design/wireframes/s-01-reading-capture.html` in structure and states, at 360 px and 1024 px.
- Verify:
  - [ ] The bound scenarios pass
  - [ ] ReadingForm shows default, focus, disabled, offline-queued and error with the styleguide's messages

### Unit 9 — Schema for anomalies

- Goal: The database has `anomaly` with one row per reading at most.
- Repository: fieldco/reading-api
- Boundary: `app/db/`
- Build phase: 2
- Depends on: 1
- Dependencies: none
- Cites: PRD §Objects; TRD §6. Data model (MER)
- Scenarios: none: enabling unit for units 10 and 11
- Verifiable result: The migration adds `anomaly` with a unique `reading_id` and applies on phase 1's schema.
- Verify:
  - [ ] The migration applies and rolls back on a copy of the phase 1 schema

### Unit 10 — Range check, queue and decisions

- Goal: Out-of-range readings become anomalies within 5 min, and only a planner can decide them.
- Repository: fieldco/reading-api
- Boundary: `app/anomalies/`
- Build phase: 2
- Depends on: 4, 9
- Dependencies: none
- Cites: PRD §Capability 2 — Anomaly review (FR-2.1, FR-2.3); TRD §8. Endpoint map
- Scenarios: `features/anomaly-review/flag-anomaly.feature` @SC-4; `features/anomaly-review/review-queue.feature` @SC-6
- Verifiable result: A reading of 9.1 bar for a 4.0 to 9.0 asset appears in `GET /v1/anomalies`; an inspector's decision returns 403.
- Verify:
  - [ ] The bound scenarios pass
  - [ ] Worker lag stays under 5 min at 20 readings per second on staging

### Unit 11 — Anomaly summaries

- Goal: Each anomaly gets a validated one-line summary, or none when the call fails.
- Repository: fieldco/reading-api
- Boundary: `app/summaries/`
- Build phase: 2
- Depends on: 10
- Dependencies: none
- Cites: PRD §Capability 2 — Anomaly review (FR-2.2); TRD §10. AI orchestration and protocols; TRD §11. MLOps
- Scenarios: `features/anomaly-review/flag-anomaly.feature` @SC-5
- Verifiable result: The summary's value, unit and delta equal the computed ones; a timeout stores the anomaly with a null summary.
- Verify:
  - [ ] The bound scenario passes
  - [ ] The reference-set eval scores ≥ 98%
  - [ ] `lint-imports --config evals/tech/boundaries/importlinter.ini` (INV-5)

### Unit 12 — Corrections with revisions

- Goal: A planner corrects a reading's value; the original is kept and the range is checked again.
- Repository: fieldco/reading-api
- Boundary: `app/readings/`
- Build phase: 2
- Depends on: 10
- Dependencies: none
- Cites: PRD §Capability 2 — Anomaly review (FR-2.4); PRD §Capability 1 — Reading capture (FR-1.5); TRD §8. Endpoint map
- Scenarios: none: no feature-level scenario; the Planner adds `@AC` scenarios for the correction in its spec
- Verifiable result: `PATCH /v1/readings/{id}` by a planner writes a `reading_revision` row; the same call by an inspector returns 403.
- Verify:
  - [ ] `pytest evals/tech/invariants/test_inv_4_revision_on_correction.py`
  - [ ] Integration test: correct into range closes nothing; correct out of range raises an anomaly

### Unit 13 — Review Queue screen

- Goal: S-02 lists open anomalies with range and summary, and lets a planner confirm or dismiss.
- Repository: fieldco/reading-web
- Boundary: `src/review/`
- Build phase: 2
- Depends on: 5, 6, 10
- Dependencies: none
- Cites: PRD §Capability 2 — Anomaly review (FR-2.3); TRD §4. Component map
- Scenarios: `features/anomaly-review/review-queue.feature` @SC-7
- Verifiable result: S-02 matches `docs/design/wireframes/s-02-review-queue.html` in structure and states; an inspector sees disabled DecisionButtons.
- Verify:
  - [ ] The bound scenario passes
  - [ ] AnomalyTable shows loading, empty and error with the styleguide's messages

## Dependencies per build phase

| Phase | Repository | Package | Needed by |
| --- | --- | --- | --- |
| 1 | fieldco/reading-api | `psycopg@3.2.3` | Unit 1 |
| 1 | fieldco/reading-api | `httpx@0.27.2` | Unit 2 |
| 1 | fieldco/reading-api | `fastapi@0.115.0` | Unit 3 |
| 1 | fieldco/reading-web | `vitest@2.1.4` | Unit 5 |
| 1 | fieldco/reading-web | `react@18.3.1` | Unit 6 |
| 1 | fieldco/reading-web | `idb@8.0.2` | Unit 7 |
