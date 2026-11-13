# Build plan — <Product name>

<Mon D, YYYY> · mode <new|delta> · traces to PRD v<x.y> and TRD v<x.y>

## Build phases

| Phase | Goal | Units | Exit check |
| --- | --- | --- | --- |
| 1 | <what a person can see working> | 1–<n> | <a number or a named scenario> |

## Units

### Unit 1 — <Name>

- Goal: <what exists after this unit that did not before>
- Repository: <owner/name>
- Boundary: `<folder/>`
- Build phase: 1
- Depends on: none
- Dependencies: <`name@version`, … | none>
- Cites: PRD §<heading> (<FR-n.m>); TRD §<n. heading>
- Scenarios: <`features/<capability>/<feature>.feature` @SC-n | none: <why>>
- Verifiable result: <one observable sentence>
- Verify:
  - [ ] <a command, a scenario or an observation>

## Dependencies per build phase

| Phase | Repository | Package | Needed by |
| --- | --- | --- | --- |
| 1 | <owner/name> | `<name@version>` | Unit <n> |
