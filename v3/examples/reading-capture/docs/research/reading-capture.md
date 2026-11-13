# Research — Reading Capture

Nov 11, 2026 · brief B-001 · mode new · English

Fictional exemplar: the product, people and URLs are invented to show the shape.

## Question tree

- Product
  - Who records readings, and how often? → answered in Personas
  - What happens to a reading after it is recorded? → answered in Customer blueprint
  - Which readings count as anomalies? → q1
- Technical
  - Which system owns the list of assets? → answered in Customer blueprint
  - Must the product work with no signal? → answered in User journey (today)
- Design
  - Which devices do inspectors carry? → answered in Personas
- Process
  - Who signs off a corrected reading? → q2

## Personas

| Persona | Context | Goal | Top pains | Current tools | Frequency | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Field Inspector | Walks plant rooms with a phone, gloves on, often with no signal | Record every reading on the route before the shift ends | Paper forms retyped later; no signal in plant rooms | Paper form, spreadsheet | 40 readings per shift | https://example.com/interviews/inspectors-2026-10 |
| Maintenance Planner | Desk role, plans work orders from readings | See abnormal readings the same day | Readings arrive 2 days late; typos hide real anomalies | Spreadsheet, Asset Registry | 3 reviews per day | https://example.com/interviews/planners-2026-10 |

## User journey (today)

| Step | Persona | Action | Touchpoint | Pain | Time | Source |
| --- | --- | --- | --- | --- | --- | --- |
| J-1 | Field Inspector | Collects the printed route for the shift | Print room | Routes change after printing | 10 min | https://example.com/interviews/inspectors-2026-10 |
| J-2 | Field Inspector | Finds the asset and reads its tag | Asset tag | Tags are worn; wrong asset picked | 2 min per asset | https://example.com/interviews/inspectors-2026-10 |
| J-3 | Field Inspector | Records the reading on site | Paper form | No signal; handwriting misread later | 1 min per asset | https://example.com/interviews/inspectors-2026-10 |
| J-4 | Field Inspector | Retypes the form into the spreadsheet | Office PC | Double entry; typos | 45 min per shift | https://example.com/interviews/inspectors-2026-10 |
| J-5 | Maintenance Planner | Scans the spreadsheet for abnormal values | Spreadsheet | Late and error-prone | 30 min per day | https://example.com/interviews/planners-2026-10 |

## Customer blueprint

| Step | Frontstage | Backstage | Support system | Failure point | Source |
| --- | --- | --- | --- | --- | --- |
| J-1 | Inspector picks up the route | Planner exports assets due this week | Asset Registry | Export is manual and weekly | https://example.com/docs/asset-registry-export |
| J-4 | Inspector submits the shift's readings | Readings are matched to assets by tag number | Asset Registry | Unknown tag numbers are dropped silently | https://example.com/docs/asset-registry-export |
| J-5 | Planner sees abnormal readings | Thresholds per asset type are applied by hand | Asset Registry | Thresholds live in one person's head | https://example.com/interviews/planners-2026-10 |

## Competitors and references

| Name | Kind | Does well | Gets wrong | Verdict | Source |
| --- | --- | --- | --- | --- | --- |
| RouteLog | product | Offline capture with a sync queue | No anomaly review; export only | differentiate | https://example.com/routelog |
| open-inspect | open-source | Tag scanning by camera | Needs a constant connection | avoid | https://example.com/open-inspect |
| WCAG 2.2 | standard | Target size and contrast rules for gloved, outdoor use | — nothing relevant | adopt | https://www.w3.org/TR/WCAG22/ |

## Constraints

- Readings are operational records kept for 5 years — https://example.com/policy/records-retention
- The Asset Registry exposes a read-only REST API with a limit of 60 requests per minute — https://example.com/docs/asset-registry-api
- Inspectors use company Android phones, 360 px wide — https://example.com/it/device-standard

## Findings

- 12% of retyped readings differ from the paper form — https://example.com/audits/readings-2026-q3
- Plant rooms on 3 of 5 sites have no mobile signal — https://example.com/it/coverage-survey
- Planners act on an abnormal reading within 1 day when they see it the same day — https://example.com/interviews/planners-2026-10

## Discovery questions

| ID | Kind | Question | Blocking | Default if unanswered |
| --- | --- | --- | --- | --- |
| q1 | product | Should anomaly thresholds come from the Asset Registry or be set in this product? | yes | — |
| q2 | process | Who may correct a reading after it syncs: the inspector, the planner, or both? | no | The planner only, with the original value kept |
