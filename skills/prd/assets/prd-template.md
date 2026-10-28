# PRD — <Product name>

<Mon D, YYYY> · <author> · v1.0

## Summary

<One paragraph: what the product turns into what; the three to five things a user does; the design principle in one clause.>

<N> capabilities, <one content model, one audit trail>:

| Capability | What the user does | What the system guarantees |
| --- | --- | --- |
| | | |

## Problem and goals

<What is wrong today, with checkable facts; who suffers; what they cannot do.>

Goals, measurable at <12 months> after launch:

| Goal | Target | Measure |
| --- | --- | --- |
| | | |

Non-goals: <what this product is not; ≥ 2 items>.

## Users and personas

<Persona count and where the set comes from.>

| Persona | Who | Primary use | Must have |
| --- | --- | --- | --- |
| | | | |

<Account model: organisational vs individual; identity requirements and the reason.>

## Capability 1 — <Name>

<What it is; what it is built from or modelled on; what it is not.>

Requirements:

- <Behaviour, condition, observable outcome; numbers where they exist.>
- <What the system does when the guarantee would be violated.>
- <…>
- <…>
- <…>

Limits: <the boundary>.

Screens: <Screen-Id, Screen-Id>.

## Capability 2 — <Name>

<…>

```mermaid
flowchart LR
```

<One-line principle: what the automated part decides and what a person decides.>

Requirements:

- <…>
- <…>
- <…>
- <…>
- <…>

Limits: <…>.

Screens: <…>.

## <Instrument name, e.g. Evidence grading rubric>

<Scoring principle; what the tiers extend.>

| Tier | Examples | Base score |
| --- | --- | --- |
| A — <name> | | 100 |
| U — Unverifiable | <cannot be opened; not supplied> | 0 |

Adjustments, applied multiplicatively to the base score:

| Factor | Rule | Multiplier |
| --- | --- | --- |
| | | |

Decision thresholds (initial values; recalibrated <cadence> against <calibration data>):

| <Class> | Accept ≥ | Floor (decline below) |
| --- | --- | --- |
| | | |
| <Safety, structure, the instrument itself> | Human always | — |

Worked examples:

- <Case: tier, factors; arithmetic = result vs threshold → outcome.>
- <Case that lands between floor and threshold → request more, naming the tier that would suffice.>
- <Case where a human overrides; the override is recorded.>

The <instrument> is versioned and published in the product; changes to it are a <human>-only class and are announced.

## Architecture

<What the product is built on; where the design documents are.>

| Product component | <Reference> component | Role in the product |
| --- | --- | --- |
| | | |

<Pipeline: source of truth; release model; how changes flow back; the regression gate.>

<Deployment: tenancy; isolation of untrusted compute; where model calls go; residency and the regulation that requires it.>

## Non-functional requirements

| Area | Requirement |
| --- | --- |
| Security | |
| Privacy | |
| Cost control | |
| Performance | |
| Availability | |
| Accessibility | |
| Languages | |
| Auditability | |
| Content integrity | |

## Metrics and success criteria

<N> headline numbers, reviewed <monthly>; the rest are leading indicators.

| Metric | Definition | Target at <12 months> |
| --- | --- | --- |
| | | |

Leading indicators: <each with its threshold and the action it triggers>.

What is not measured: <metrics deliberately absent> — <the one reason>.

## Scope, phases, and release plan

<N> phases, each shippable, each adding one capability on the previous one's <foundation>.

| Phase | Ships | Gate to next |
| --- | --- | --- |
| 1 — <name> | | |

Out of scope for the first release: <…>.

Dependencies: <each with its current state>.

## Risks and open questions

| Risk | Mitigation |
| --- | --- |
| | |

Open questions:

- <A decision not yet made, with its options?>
- <…>
- <…>
