# Mermaid patterns for a TRD

Every diagram is Mermaid in a fenced ` ```mermaid ` block, so it renders in docs, GitHub and most wikis without a tool. Each pattern below is a skeleton with the conventions the TRD relies on; copy, rename, prune.

One rule for all of them: the diagram shows what exists, the paragraph after it states what cannot happen. A diagram without its invariant paragraph is decoration.

## C4 context (§2.1)

```mermaid
C4Context
  title System context · v0.1 · PRD §Users, §Architecture
  Person(persona1, "Persona name", "What they do here")
  Person(persona2, "Persona name", "What they do here")
  System(product, "Product name", "Capability 1 · Capability 2 · Capability 3")
  System_Ext(sot, "Source of truth", "Where content/data is authored; what the product reads from it")
  System_Ext(providers, "Model providers", "Reached only through the gateway")
  System_Ext(idp, "Customer IdP", "SAML / OIDC")
  System_Ext(ci, "CI", "What it runs and when")
  Rel(persona1, product, "verb")
  Rel(product, sot, "verb; verb")
  Rel(product, providers, "model calls via gateway")
  Rel(ci, product, "results webhook")
```

Conventions: one `Person` per PRD persona, no more; every `System_Ext` that appears here appears again as a conduit in §3.1; `Rel` labels are verbs, not nouns.

## C4 container (§2.2)

```mermaid
C4Container
  title Containers · v0.1 · PRD §Architecture
  Person(user, "User", "any persona")
  System_Boundary(b, "Product · <region>") {
    Container(web, "App", "framework", "what it serves; API")
    ContainerDb(db, "Database", "engine + extensions", "what it holds")
    Container(wf, "Workflow engine", "product", "which workflows")
    Container(pdp, "Policy", "product", "what it decides; fail-closed")
    Container(gw, "Model gateway", "product", "budgets, routing, pinning")
    Container(workers, "Workers", "runtime", "which agents and sensors")
    ContainerDb(obj, "Object storage", "S3 API", "what it holds")
    Container(obs, "Observability", "stack", "traces, cost, dashboards")
  }
  System_Ext(sot, "Source of truth")
  System_Ext(prov, "Model providers")
  Rel(user, web, "HTTPS")
  Rel(web, db, "ORM")
  Rel(web, wf, "start / signal")
  Rel(web, pdp, "authorise")
  Rel(workers, gw, "model calls")
  Rel(gw, prov, "HTTPS, pinned versions")
```

Conventions: the boundary name carries the region; the container count equals the count in §2's intro sentence; the `Rel` from workers to gateway (not from web) is the one that keeps provider credentials out of request threads — draw it that way when it is true, and say so in the paragraph.

## Deployment (§2.4)

```mermaid
flowchart TB
  subgraph R1[Region: <name> · residency boundary]
    subgraph WEB[Web tier · multi-tenant]
      N[App × n]
      W[Workers × n]
    end
    subgraph CP[Control plane]
      T[Workflow engine]
      P[Policy]
      I[Identity]
      G[Model gateway]
    end
    subgraph DATA[Data tier · private subnet]
      DB[(Database primary + replica)]
      S3[(Object storage)]
      OB[Observability]
    end
    subgraph ISO[Isolated pool · separate VPC]
      X[Sandbox host × m]
    end
  end
  subgraph R2[Region: <name> · not offered at launch]
    D[disabled]
  end
  N --> DB
  W --> G
  N --> X
  X -. signed URL .-> S3
```

Conventions: a region the PRD mentions but does not ship is drawn with a `disabled` node, so the reviewer sees it was considered; a dotted edge marks the only path out of an isolated pool.

## Network topology (§3) and the riskiest path (§3.2)

```mermaid
flowchart LR
  U[Users] -->|443| EDGE[Public edge<br/>WAF · TLS · rate limit]
  EDGE -->|443| WEB[Web tier]
  WEB -->|5432 mTLS| DATA[(Data tier)]
  WEB -->|7233 mTLS| CTRL[Control plane]
  WEB -->|4000 mTLS| GW[Gateway]
  GW -->|443 egress allow-list| PROV[Model providers]
  WEB -->|8443 mTLS| SBXC[Isolated-pool control API]
  SBXC --> SBX[Isolated pool · no inbound]
  SBX -->|443 allow-list only| REG[named registries]
  SBX -. denied .-> X[everything else → logged]
  CI[CI] -->|443 webhook + HMAC| EDGE
```

```mermaid
flowchart LR
  P[untrusted code] --> T[interface]
  T --> N{enforcement point<br/>default DROP}
  N -->|dst in allow-list · 443| OK[forward]
  N -->|else| D[DROP + log]
  D --> L[(denial record<br/>session · dst · ts)]
  L --> UI[where a person sees it]
```

Conventions: every edge label carries port and auth; a dotted edge is a denial; the riskiest-path diagram ends at the place a human sees the denial.

## Entity–relationship (§4.1)

```mermaid
erDiagram
  Organisation ||--o{ User : has
  User ||--o{ Session : opens
  Release ||--o{ EntityVersion : pins
  Entity ||--o{ EntityVersion : versions
  EntityVersion ||--o{ Child : has
  Suggestion ||--|| Anchor : anchored_to
  Suggestion ||--|{ Evidence : supports
  Suggestion ||--|{ LedgerRecord : chained
```

Conventions: labels are verbs or verb phrases; `||--||` for a required 1:1 that enforces a PRD rule (*no free-text suggestion* becomes a required `Anchor`); the bridge entity (the one that hangs off two domains) is named in the paragraph.

## Pipeline flowchart (§2.3, §4.5)

```mermaid
flowchart LR
  S[Intake] --> I[Cheap sensors<br/>schema · exists · parses]
  I -->|fail| D0[Declined at intake<br/>no model call]
  I --> G[Grader]
  G -->|score < floor| D0
  G --> C[Consistency sensors]
  C --> A{Judgment}
  A -->|accept| M[Merge]
  A -->|request more| R[Named tier]
  A -->|decline| D1[Named sensor or reason]
  A -->|human class| H[Human queue]
  H --> M
  M --> L[(Audit record)]
  R --> L
  D1 --> L
  D0 --> L
```

Conventions: cheap sensors before any model call; every outcome, including intake declines, reaches the audit record; the gate node (`{}`) is the one the paragraph's invariant is about.

## Sequence (§7)

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant W as Route
  participant S as Sensor (before)
  participant G as Gateway
  participant V as Sensor (after)
  participant J as Grader (isolated)
  participant L as Audit record
  U->>W: request
  W->>S: cheap check
  alt out of scope
    S-->>W: refusal cause
    W-->>U: refusal + pointer
    W->>L: record (refusal)
  else in scope
    W->>G: draft
    G-->>U: token stream
    W->>V: verify each claim
    V-->>W: per-claim verdicts
    W->>J: grounded? (sees only answer + sources)
    J-->>W: score
    alt score < threshold
      W->>G: one repair pass (cap 1)
      G-->>W: revised draft → V again
    end
    W-->>U: final event: citations, verdicts, trace id
    W->>L: record (citations, verdicts, guide, model)
  end
```

```mermaid
sequenceDiagram
  autonumber
  participant O as Orchestrator
  participant V as Isolated runtime
  participant D as Verdict engine
  O->>V: run
  par watchdog
    O->>V: kill at wall-clock N s or memory > M GiB
    V-->>O: KILLED + message
  and egress
    V--xO: request to non-allow-listed host → dropped, counted
  end
  V-->>D: printed results
  D->>D: compare outside the runtime
```

Conventions: `autonumber` always; `alt` for every failure branch; `par` for watchdogs; the cap is written in the message (`cap 1`); the isolated grader "sees only" what the paragraph says it sees; the verdict is computed outside the untrusted runtime.

## Authorisation (§6.2)

```mermaid
flowchart LR
  R[Route handler] --> Q[Policy input:<br/>subject · action · resource · context]
  Q --> P{Policy<br/>default deny}
  P -->|allow| H[Handler runs]
  P -->|deny| E[403 + decision log]
  P -->|policy unreachable| E
```

Convention: the `unreachable` edge is drawn, because fail-closed is a claim the diagram must make visible.

## Integrations (§7, last flow)

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser
  participant N as App
  participant K as Identity broker
  participant I as Customer IdP
  participant GW as Gateway
  rect rgb(240,240,236)
  note over B,I: SSO login
  B->>N: /login (org)
  N->>K: OIDC authorize
  K->>I: SAML / OIDC
  I-->>K: assertion
  K-->>N: id token (org, role claims)
  N-->>B: session cookie
  end
  rect rgb(240,240,236)
  note over N,GW: Metered call
  N->>GW: call (virtual key)
  alt budget remaining
    GW-->>N: completion + usage
  else cap reached
    GW-->>N: 402 budget_exceeded
  end
  end
```

Convention: one `rect` per integration, each with one owner named in the paragraph (*identity is the broker's, budgets are the gateway's, state is the workflow engine's*).
