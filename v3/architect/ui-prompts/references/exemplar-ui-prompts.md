# UI brief — Reading Capture

Nov 11, 2026 · traces to PRD v1.0 · path wireframes

Fictional exemplar.

## Journey maps

One map per PRD persona: the steps of their journey with the product, the screen each happens on, and how it feels, scored from -2 (worst) to +2 (best). Every negative step has a pain point and the design response that answers it.

### Field Inspector — inspector

| Step | Stage | Screen | Action | Result | Feeling | Pain point | Design response | Next |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Arrive at the asset | S-01 | Enters the asset tag | The asset's type and unit appear under the tag | 0 neutral | — | — | 2 |
| 2 | Record | S-01 | Enters the value and saves | The reading joins today's list, marked synced or unsent | +1 quick | — | — | 1 or end |
| 2a | Record | S-01 | Saves with an unknown tag | The form shows the tag-not-found message and keeps the value | -1 stuck | Typed value at risk; no one to ask in the plant room | Keep the value on screen; the message says what to do next | 1 |
| 3 | No signal | S-01 | Saves in a plant room with no signal | The reading shows Unsent with an icon, then Synced | -1 unsure | Not knowing whether a reading was lost | The Unsent badge and its sentence say the reading is safe on the phone | 1 or end |

### Maintenance Planner — planner

| Step | Stage | Screen | Action | Result | Feeling | Pain point | Design response | Next |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Start the day | S-02 | Opens the queue | Open anomalies listed with tag, value, range and summary | +1 oriented | — | — | 2 |
| 2 | Decide | S-02 | Confirms or dismisses one | The row leaves the queue; the decision keeps the planner's id | +2 done | — | — | 1 or end |
| 2a | Decide | S-02 | Opens an anomaly whose summary failed | The row shows "Summary unavailable" with value, unit and range | -1 slowed | Has to work out the difference by hand | Value, unit and range always shown beside the summary | 2 |

## Screen prompts

### S-01 — Reading Capture

- Purpose: Record a reading against an asset, online or offline.
- Roles: inspector; a planner who opens it sees "This screen is for inspectors."
- Shows: Reading.asset_tag "PMP-0412", Asset.type "pump", Asset.unit "bar", Reading.value "7.25", today's readings with value, unit, tag and status.
- Actions: Save reading → the reading joins today's list → stays on S-01 with the tag field focused.
- Layout: title; ReadingForm (tag, asset line, value, save); ReadingList below.
- Mobile view: designed at 360 px first: one column, the value field uses type.value, the save button spans the width and is 56 px tall; every target ≥ 44 × 44 px. At 1024 px the list moves beside the form.
- States: ReadingForm: default, focus, disabled, offline-queued, error; ReadingList: default, empty
- Prompt: A phone screen for a field inspector wearing gloves. One column, large type. A tag field, a line showing the asset's type and unit, a large numeric value field and a full-width save button. Below, today's readings, each marked synced or unsent with an icon and a word. Show the offline-queued and tag-not-found states. Use the styleguide tokens; no brand colours.

### S-02 — Review Queue

- Purpose: Decide each flagged reading.
- Roles: planner; an inspector sees the table without DecisionButtons.
- Shows: Anomaly.summary "7.25 bar is 0.4 above this pump's 30-day mean", Reading.value "9.10", Asset.tag "PMP-0412", Asset.range_min "4.0", Asset.range_max "9.0", Reading.captured_at "2026-11-11T08:42:10-03:00".
- Actions: Confirm → the anomaly is confirmed and leaves the queue → S-02; Dismiss → the anomaly is dismissed and leaves the queue → S-02.
- Layout: title with the open count; AnomalyTable with one row per anomaly; DecisionButtons at the end of each row.
- Mobile view: at 360 px each row becomes a card with the summary first and DecisionButtons full width below it, each 48 px tall; at 1024 px the table shows all columns.
- States: AnomalyTable: default, loading, empty, error; DecisionButtons: default, focus, disabled
- Prompt: A desktop review queue for a maintenance planner. A dense table of flagged readings: asset tag, value with unit, the allowed range, a one-line summary and the capture time. Confirm and Dismiss at the end of each row. Show loading, empty and error states, and the disabled buttons an inspector sees. Use the styleguide tokens; no brand colours.

## UI scenarios

| Screen | Scenario | Feature file |
| --- | --- | --- |
| S-01 | Recording a reading takes at most 3 taps | `features/reading-capture/capture-reading.feature` |
| S-01 | An unknown tag is refused with the next step | `features/reading-capture/capture-reading.feature` |
| S-02 | The planner sees the anomaly with the asset's range | `features/anomaly-review/review-queue.feature` |
