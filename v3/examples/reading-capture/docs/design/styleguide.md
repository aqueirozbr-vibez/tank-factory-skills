# Styleguide — Reading Capture

Nov 11, 2026 · source open-source defaults (no brand tokens in the brief)

Fictional exemplar.

## Tokens

| Token | Category | Value | Use |
| --- | --- | --- | --- |
| color.ground | colour | #ffffff | Page background |
| color.ink | colour | #17202a | Text and icons |
| color.muted | colour | #5b6773 | Secondary text |
| color.primary | colour | #1f5fa8 | Primary action |
| color.on-primary | colour | #ffffff | Text on the primary action |
| color.line | colour | #c9d1d9 | Borders and dividers |
| color.danger | colour | #a4262c | Errors |
| color.warn | colour | #7a5200 | Offline and unsent |
| color.ok | colour | #1e6b3a | Synced |
| type.body | type | 16px/24px 400 Inter | Body text |
| type.label | type | 14px/20px 500 Inter | Labels and table headers |
| type.title | type | 22px/28px 600 Inter | Screen titles |
| type.value | type | 28px/36px 600 Inter | The reading value field |
| space.1 | spacing | 4px | Icon to label |
| space.2 | spacing | 8px | Inside controls |
| space.4 | spacing | 16px | Between controls |
| space.6 | spacing | 24px | Between groups |
| radius.control | radius | 6px | Inputs and buttons |
| elevation.none | elevation | none | Everything; borders carry structure |
| motion.state | motion | 120ms ease-out | State changes |

## Fonts and icons

| Asset | Family | License |
| --- | --- | --- |
| Text | Inter | OFL-1.1 |
| Icons | Lucide | ISC |

## Breakpoints

| Name | Min width | Layout change |
| --- | --- | --- |
| phone | 360 px | One column; the save button spans the width and stays above the keyboard |
| desktop | 1024 px | Review Queue shows the table with the detail panel beside it |

## Components

| Component | Use | Interactive |
| --- | --- | --- |
| ReadingForm | Tag, value and save on S-01 | yes |
| ReadingList | Today's readings on S-01 | no |
| AnomalyTable | Open anomalies on S-02 | yes |
| DecisionButtons | Confirm or dismiss on S-02 | yes |

## Component states

| Component | State | Appearance | Message |
| --- | --- | --- | --- |
| ReadingForm | default | color.line border, color.ink text | — |
| ReadingForm | hover | color.primary border | — |
| ReadingForm | focus | 2px color.primary outline with a 2px gap | — |
| ReadingForm | disabled | color.muted text, save button inactive | — |
| ReadingForm | offline-queued | color.warn badge with an icon and the word "Unsent" | Saved on this phone. It will send when you are back online. |
| ReadingForm | error | color.danger border and icon | Tag not found. Check the tag or ask your planner. |
| ReadingList | default | Rows with value, unit, tag and a synced or unsent label | — |
| ReadingList | empty | color.muted text, no rows | No readings yet today. |
| AnomalyTable | default | Rows with tag, value, range and summary | — |
| AnomalyTable | hover | Row background color.line at 30% | — |
| AnomalyTable | focus | 2px color.primary outline on the row | — |
| AnomalyTable | disabled | color.muted rows while a decision saves | — |
| AnomalyTable | loading | 3 skeleton rows | — |
| AnomalyTable | empty | color.muted text, no rows | Nothing to review. |
| AnomalyTable | error | color.danger text above the table | Could not load anomalies. Try again. |
| DecisionButtons | default | Confirm in color.primary, Dismiss outlined | — |
| DecisionButtons | hover | Darker fill or border | — |
| DecisionButtons | focus | 2px color.primary outline with a 2px gap | — |
| DecisionButtons | disabled | color.muted, shown to roles that cannot decide | — |
