# Project overview — Reading Capture

## Product

Reading Capture lets field inspectors record meter readings on a phone, with or without signal, and shows maintenance planners the abnormal ones the same day. It replaces a paper form retyped into a spreadsheet. A reading saved on a device is never lost, and no anomaly is closed without a named planner.

Product kind: ui_and_service

## Users and roles

| Role | Persona | Does |
| --- | --- | --- |
| inspector | Field Inspector | Records readings on S-01; reads own readings |
| planner | Maintenance Planner | Decides anomalies on S-02; corrects readings |

## Features

| Feature | Capability | Feature file |
| --- | --- | --- |
| `capture-reading` | 1 — Reading capture | `features/reading-capture/capture-reading.feature` |
| `offline-queue` | 1 — Reading capture | `features/reading-capture/offline-queue.feature` |
| `flag-anomaly` | 2 — Anomaly review | `features/anomaly-review/flag-anomaly.feature` |
| `review-queue` | 2 — Anomaly review | `features/anomaly-review/review-queue.feature` |

## Scope

- In scope: phase 1 (Reading capture), then phase 2 (Anomaly review).
- Non-goals: work-order management; editing the asset list; reading meters automatically; iOS; photos; notifications.

## Principles

| Article | Principle | Compliance check |
| --- | --- | --- |
| P-1 | A reading is never silently dropped | conformance check: every reading the API acknowledges has a stored row (INV-1) |
| P-2 | The Asset Registry is the only source of assets; this product never writes to it | conformance check: only the registry client calls the Asset Registry, and only to read (INV-3) |
| P-3 | Every change to a reading keeps the original value and the person who changed it | review question: does the diff write to `reading` without a `reading_revision` row? |
| P-4 | Capture works with gloves on a 360 px phone | review question: is every new target on S-01 ≥ 44 × 44 px? |

## Glossary

| Name | Kind | Defined in |
| --- | --- | --- |
| Field Inspector | persona | PRD §Users and personas |
| Maintenance Planner | persona | PRD §Users and personas |
| inspector, planner | role | PRD §Users and personas |
| S-01 Reading Capture | screen | PRD §Journeys and screens |
| S-02 Review Queue | screen | PRD §Journeys and screens |
| Reading, Asset, Anomaly | object | PRD §Objects |
| ReadingForm, ReadingList, AnomalyTable, DecisionButtons | component | `docs/design/styleguide.md` |
| offline-queued | state | `docs/design/styleguide.md` |
| Asset Registry | external system | TRD §9. Integration sequences |
| anomaly_summary | model call | TRD §10. AI orchestration and protocols |

## Documents

- PRD: `docs/prd/reading-capture.md` v1.0
- TRD: `docs/trd/reading-capture.md` v1.0
- Design: `docs/design/styleguide.md`, `docs/design/wireframes/`
- Build plan: `specs/00-build-plan.md`
