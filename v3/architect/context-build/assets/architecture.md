# Architecture — <Product name>

Compiled from `docs/trd/<product>.md` v<x.y>. Cite TRD sections by heading for detail.

## Stack

| Repository | Language | Package manager | Base image | Frameworks and libraries |
| --- | --- | --- | --- | --- |
| <owner/name> | <language version> | <manager version> | <image> | <framework, key libraries> |

## Boundaries

One boundary per unit of work. A change that needs two boundaries is two units.

| Boundary | Folder | Responsibility | May import | Never imports |
| --- | --- | --- | --- | --- |
| <component> | `<folder/>` | <one line> | `<folder/>` | `<folder/>` |

## Invariants

These hold on every commit. Each has a check that fails when it is broken.

| ID | Invariant | Check |
| --- | --- | --- |
| INV-1 | <statement> | `evals/tech/<path>` |
| INV-2 | <statement> | `evals/tech/<path>` |
| INV-3 | <statement> | `evals/tech/<path>` |
| INV-4 | <statement> | `evals/tech/<path>` |

## Data

- <entity>: <one line> — TRD §6. Data model (MER)

## Interfaces

- Endpoints: <groups> — TRD §8. Endpoint map
- Integrations: <systems> — TRD §9. Integration sequences
- Model calls: <calls, or none> — TRD §10. AI orchestration and protocols
