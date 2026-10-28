# TRD — <Product name>

<Mon D, YYYY> · <author> · v0.1 · traces to PRD <id or date> and <UI package> <version>

## 1. Purpose, scope, phases

<One sentence: the product. The phase rule: each phase adds one capability on the previous phase's components and must not pull forward components the next phase owns. Fixed stack: <…>. Every other component is decided in section 2.0 with the source it implements.>

| Phase | Adds (architecture increment) | Must not need yet | Gate to next (PRD §Scope) |
| --- | --- | --- | --- |
| 1 — <name> | | | |

Out of scope for the first release, per PRD: <…>.

Traceability rule for this document: every section names the PRD capability, non-functional row or screen it serves. A section that only restates the PRD is deleted.

## 2. C4 diagrams

<Count the top-level pieces in one sentence.>

### 2.0 Component decisions (PRD §Architecture)

| Component | Candidates | Pick | Why (≤ 5 lines) | Source |
| --- | --- | --- | --- | --- |
| | | | | |

### 2.1 System context (PRD §Users and personas, §Architecture)

```mermaid
C4Context
  title System context · v0.1 · PRD §Users, §Architecture
```

<≤ 3 sentences: boundary invariants.>

### 2.2 Containers (PRD §Architecture, §Deployment)

```mermaid
C4Container
  title Containers · v0.1 · PRD §Architecture
```

<≤ 3 sentences: which container users reach; which holds credentials; what isolated pools can reach.>

### 2.3 Components per capability

| Capability | Components | PRD "must have" it carries | Screen |
| --- | --- | --- | --- |
| | | | |

```mermaid
flowchart LR
```

<One paragraph: the invariant the pipeline protects.>

### 2.4 Deployment (PRD §Deployment, §Non-functional · Privacy)

```mermaid
flowchart TB
```

<Tenancy model; which pool has no route to data.>

## 3. Network topology

<Zone count; default stance; what can never reach what (PRD §…).>

```mermaid
flowchart LR
```

### 3.1 Conduits

| From | To | Protocol · port | Direction | Auth | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

### 3.2 <Riskiest path>

```mermaid
flowchart LR
```

<Where the rule lives; where a denial surfaces to a person.>

### 3.3 Residency boundary

<…>

### 3.4 Secrets and the model-visible surface

| Secret | Lives in | Reachable by | Model-visible |
| --- | --- | --- | --- |
| | | | |

Proof: <which fields each model-backed component receives (section 8); nothing from env, headers or config is serialised into a prompt; scanner in CI and at log ingestion; required count zero.>

## 4. Data model

<One datastore sentence; domains; the immutability rule.>

### 4.1 Entity–relationship diagram (PRD §Capability …)

```mermaid
erDiagram
```

<Reading order; the bridge entity.>

### 4.2 Schema

```<language>
```

Rules the schema enforces, with the PRD line each serves:

| Rule | Mechanism |
| --- | --- |
| | |

### 4.3 Integrity specification (PRD §Non-functional · Auditability)

- Canonical form: <…>
- Hash: <…>
- Chain scope: <…>
- What a record covers: <…>
- Verification: <…>
- Export: <…>

### 4.4 Retention and deletion (PRD §Non-functional · Privacy)

| Data | Retention | Mechanism |
| --- | --- | --- |
| | | |

### 4.5 Ingestion pipeline (PRD §Capability …)

```mermaid
flowchart LR
```

- Idempotency: <…>
- Migrations: <…>
- Seeding: <…>
- Flow back: <…>

## 5. Front end

<The spine sentence. Every screen in the UI package maps to one route below.>

### 5.1 Route map

| Route | Screen (UI package) | Rendering | Auth |
| --- | --- | --- | --- |
| | | | |

<Responsive rule.>

### 5.2 Component tree and data fetching

| Layer | Server components | Client components |
| --- | --- | --- |
| | | |

- Cache keying and invalidation: <…>
- Pre-rendering: <…>
- Streaming transport: <…>
- i18n: <…>
- Accessibility: <…>
- Keyboard map: <…>

### 5.3 State

| State | Lives in |
| --- | --- |
| | |

### 5.4 Performance budgets (PRD §Non-functional · Performance)

| Budget | Mechanism |
| --- | --- |
| | |

## 6. Back end

<API style; contract source; long-running work; base path; the auth and policy gate.>

### 6.1 Endpoint catalogue

| Method · path | Auth · role | Request → response | Rate limit | Idempotency | Errors |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Error body everywhere: `{code, message, detail?, traceId}`; messages are declarative and name the fix, in the user's language.

### 6.2 Authorisation model

```mermaid
flowchart LR
```

| Subject | May |
| --- | --- |
| | |

<Which rules are policy not code; where policy is versioned; failed load behaviour.>

### 6.3 Budget enforcement

- <Where the cap is enforced.>
- <Who receives no key.>
- <How the meter writes; which screens read it.>
- <What happens at the cap.>

### 6.4 Rate limits and the throttle rule

| Rule | Value | Enforced at |
| --- | --- | --- |
| | | |

## 7. Sequence diagrams

<Count; loop pattern; cap discipline; sensors before judgment.>

### 7.1 <Flow> (PRD §Capability …)

```mermaid
sequenceDiagram
  autonumber
```

<The invariant; what a user never sees.>

## 8. AI agent specifications

<Count; versioned guide, byte-stable prefix, structured output, sensors on both sides, calibration.>

|  | <Agent A> | <Agent B> |
| --- | --- | --- |
| Model tier | | |
| Guide | | |
| Prefix order (byte-stable, cached) | | |
| May read | | |
| May never read | | |
| Output schema | | |
| Sensors before | | |
| Sensors after | | |
| Cap | | |

<Where guides live; how an edit ships; what each prompt logs.>

### 8.1 Calibration (PRD §Metrics)

| Agent | Reference set | Metric | Gate | Retirement |
| --- | --- | --- | --- | --- |
| | | | | |

## 9. Observability and audit

<Conventions; what is ledgered (PRD §Non-functional · Auditability).>

| Event | Span attributes | Stored in |
| --- | --- | --- |
| | | |

Dashboards, one per PRD headline metric and one for leading indicators:

| Dashboard | Series |
| --- | --- |
| | |

Not collected, by design (PRD §What is not measured): <…>.

Audit export: <…>.

## 10. Security and threat model

<Count of attacks the PRD names (PRD §Risks).>

| Attack | Control | Source | Detection | Residual risk |
| --- | --- | --- | --- | --- |
| | | | | |

Fail-closed everywhere a decision is made: <…>.

## 11. Testing, CI/CD and environments

<The regression gate in one sentence.>

| Level | What | Tooling | Gate |
| --- | --- | --- | --- |
| Unit | | | |
| Contract | | | |
| Policy | | | |
| Integration | | | |
| End to end | | | |
| Golden sets | | | |
| Load | | | |

Environments: <…>. Promotion: <…>.

Release procedure: <step → step → step>. Rollback: <content; code; migrations>.

## 12. Open decisions and assumptions

The PRD's open questions, with the assumption this TRD builds on until they are decided.

| Question (PRD §Open questions) | Assumption used here | What changes if decided otherwise |
| --- | --- | --- |
| | | |

Decisions this document made that the PRD left open, for review: <decision (section)>; <decision (section)>.
