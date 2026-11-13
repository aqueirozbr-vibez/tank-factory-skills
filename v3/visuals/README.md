# Visuals

© 2026 Tank Factory · CC BY 4.0

Two sets of high-resolution PNGs that go with the Architect skill pack.

## `examples/` — the 28 building blocks, worked

One board per building block of the sample product Reading Capture, plus an overview and the fourteen-link handover check. Each board shows the block as it sits in the sample file (diagrams as their Mermaid text and a preview) and, beside it, what the block must contain, the test that says it is done, what it feeds, the skill and check script behind it, and a weak line rewritten into one that passes.

The boards are rendered from `examples/reading-capture/`, so they cannot drift from the sample files. After changing a sample file, run from the pack root:

```bash
npm install @fontsource-variable/instrument-sans @fontsource-variable/geist-mono @fontsource/vt323
pip install markdown playwright pyoxipng && playwright install chromium   # plus the Mermaid CLI, mmdc
python3 visuals/build_examples.py --fonts node_modules
```

The script stops if any check script fails on the sample product. Boards are 1600 px wide, rendered at 2x (3200 px).

| Block | Essential | Title | Board | Source |
| --- | --- | --- | --- | --- |
| — | — | Overview | [`00-overview.png`](examples/00-overview.png) | all |
| D1 | 01 Discovery | Personas | [`01-D1-personas.png`](examples/01-D1-personas.png) | `docs/research/reading-capture.md` |
| D2 | 01 Discovery | User Journey | [`02-D2-user-journey.png`](examples/02-D2-user-journey.png) | `docs/research/reading-capture.md` |
| D3 | 01 Discovery | Customer Blueprint | [`03-D3-customer-blueprint.png`](examples/03-D3-customer-blueprint.png) | `docs/research/reading-capture.md` |
| D4 | 01 Discovery | Competitors and References | [`04-D4-competitors-and-references.png`](examples/04-D4-competitors-and-references.png) | `docs/research/reading-capture.md` |
| P1 | 02 PRD | User Roles | [`05-P1-user-roles.png`](examples/05-P1-user-roles.png) | `docs/prd/reading-capture.md` |
| P2 | 02 PRD | Jobs to be done | [`06-P2-jobs-to-be-done.png`](examples/06-P2-jobs-to-be-done.png) | `docs/prd/reading-capture.md` |
| P3 | 02 PRD | User Journey Flowchart | [`07-P3-user-journey-flowchart.png`](examples/07-P3-user-journey-flowchart.png) | `docs/prd/reading-capture.md` |
| P4 | 02 PRD | Screens Map | [`08-P4-screens-map.png`](examples/08-P4-screens-map.png) | `docs/prd/reading-capture.md` |
| P5 | 02 PRD | Service Blueprint | [`09-P5-service-blueprint.png`](examples/09-P5-service-blueprint.png) | `docs/prd/reading-capture.md` |
| P6 | 02 PRD | Objects definitions and metadata | [`10-P6-objects-definitions-and-metadata.png`](examples/10-P6-objects-definitions-and-metadata.png) | `docs/prd/reading-capture.md` |
| P7 | 02 PRD | Functional Requirements | [`11-P7-functional-requirements.png`](examples/11-P7-functional-requirements.png) | `docs/prd/reading-capture.md` |
| P8 | 02 PRD | Non-functional requirements | [`12-P8-non-functional-requirements.png`](examples/12-P8-non-functional-requirements.png) | `docs/prd/reading-capture.md` |
| U1 | 03 UI | Journey Maps | [`13-U1-journey-maps.png`](examples/13-U1-journey-maps.png) | `docs/design/ui-prompts.md` |
| U2 | 03 UI | Design System | [`14-U2-design-system.png`](examples/14-U2-design-system.png) | `docs/design/styleguide.md` |
| U3 | 03 UI | Key Features Screens | [`15-U3-key-features-screens.png`](examples/15-U3-key-features-screens.png) | `docs/design/ui-prompts.md` |
| U4 | 03 UI | Mobile View | [`16-U4-mobile-view.png`](examples/16-U4-mobile-view.png) | `docs/design/ui-prompts.md` |
| U5 | 03 UI | Components States | [`17-U5-components-states.png`](examples/17-U5-components-states.png) | `docs/design/styleguide.md` |
| T1 | 04 TRD | DevOps | [`18-T1-devops.png`](examples/18-T1-devops.png) | `docs/trd/reading-capture.md` |
| T2 | 04 TRD | C4 Diagram | [`19-T2-c4-diagram.png`](examples/19-T2-c4-diagram.png) | `docs/trd/reading-capture.md` |
| T3 | 04 TRD | Stack | [`20-T3-stack.png`](examples/20-T3-stack.png) | `docs/trd/reading-capture.md` |
| T4 | 04 TRD | Network Topology | [`21-T4-network-topology.png`](examples/21-T4-network-topology.png) | `docs/trd/reading-capture.md` |
| T5 | 04 TRD | Endpoint Map | [`22-T5-endpoint-map.png`](examples/22-T5-endpoint-map.png) | `docs/trd/reading-capture.md` |
| T6 | 04 TRD | Component Map | [`23-T6-component-map.png`](examples/23-T6-component-map.png) | `docs/trd/reading-capture.md` |
| T7 | 04 TRD | Integration Sequence Diagrams | [`24-T7-integration-sequence-diagrams.png`](examples/24-T7-integration-sequence-diagrams.png) | `docs/trd/reading-capture.md` |
| T8 | 04 TRD | MER | [`25-T8-mer.png`](examples/25-T8-mer.png) | `docs/trd/reading-capture.md` |
| T9 | 04 TRD | Data Flow | [`26-T9-data-flow.png`](examples/26-T9-data-flow.png) | `docs/trd/reading-capture.md` |
| T10 | 04 TRD | AI Orchestration & Protocols | [`27-T10-ai-orchestration-protocols.png`](examples/27-T10-ai-orchestration-protocols.png) | `docs/trd/reading-capture.md` |
| T11 | 04 TRD | MLOps | [`28-T11-mlops.png`](examples/28-T11-mlops.png) | `docs/trd/reading-capture.md` |
| — | — | Fourteen links | [`29-handover-links.png`](examples/29-handover-links.png) | all |

## `deck/` — The Initial Context

The slides of the Tank Factory deck *The Initial Context* (23 slides), rendered at 3840 × 2160: the four essentials, the 28 blocks, the ten skills that write and check them, the context build and the handover check.
