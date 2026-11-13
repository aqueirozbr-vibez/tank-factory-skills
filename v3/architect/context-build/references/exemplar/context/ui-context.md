# UI context — Reading Capture

Compiled from `docs/design/styleguide.md`. Screens: `docs/design/wireframes/`.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| color.ground | #ffffff | Page background |
| color.ink | #17202a | Text and icons |
| color.muted | #5b6773 | Secondary text |
| color.primary | #1f5fa8 | Primary action |
| color.on-primary | #ffffff | Text on the primary action |
| color.line | #c9d1d9 | Borders and dividers |
| color.danger | #a4262c | Errors |
| color.warn | #7a5200 | Offline and unsent |
| color.ok | #1e6b3a | Synced |
| type.body | 16px/24px 400 Inter | Body text |
| type.label | 14px/20px 500 Inter | Labels and table headers |
| type.title | 22px/28px 600 Inter | Screen titles |
| type.value | 28px/36px 600 Inter | The reading value field |
| space.1 | 4px | Icon to label |
| space.2 | 8px | Inside controls |
| space.4 | 16px | Between controls |
| space.6 | 24px | Between groups |
| radius.control | 6px | Inputs and buttons |
| elevation.none | none | Everything; borders carry structure |
| motion.state | 120ms ease-out | State changes |

## Fonts and icons

- Text: Inter (OFL-1.1)
- Icons: Lucide (ISC)

## Breakpoints

| Name | Min width | Layout change |
| --- | --- | --- |
| phone | 360 px | One column; the save button spans the width |
| desktop | 1024 px | Review Queue shows the full table |

## Components and states

| Component | States |
| --- | --- |
| ReadingForm | default, hover, focus, disabled, offline-queued, error |
| ReadingList | default, empty |
| AnomalyTable | default, hover, focus, disabled, loading, empty, error |
| DecisionButtons | default, hover, focus, disabled |

## Rules

- Style only with tokens; a raw colour or size in a diff is a finding.
- State is never shown by colour alone: pair it with a word or an icon.
- Touch targets on S-01 are ≥ 44 × 44 px; the save button is 56 px tall.
- Error and empty messages use the exact text in `docs/design/styleguide.md`.
