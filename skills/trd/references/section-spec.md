# TRD section contract

Twelve sections, fixed order, fixed numbering. Each entry below says what the section is for, what it must contain (tables with their exact columns, diagram type), and the pass test the section must meet before the next one starts. Column headers are exact: `scripts/lint_trd.py` checks them.

Contents: §0 Header · §1 Purpose, scope, phases · §2 C4 diagrams · §3 Network topology · §4 Data model · §5 Front end · §6 Back end · §7 Sequence diagrams · §8 AI agent specifications · §9 Observability and audit · §10 Security and threat model · §11 Testing, CI/CD and environments · §12 Open decisions and assumptions · Cross-section tests

---

## §0 Header

- H1: `# TRD — <Product name>`
- Byline, one line: `<Mon D, YYYY> · <author> · v<major.minor> · traces to PRD <id or date> and <UI package / screen spec> <version>`

The byline is provenance. A TRD that cannot name the PRD version it traces to cannot be checked against it, and every "PRD §…" anchor in the document points at that version.

## §1 Purpose, scope, phases

Purpose: fix what is being built, in what order, and what is already decided before any component is chosen.

Contains, in order:

1. One paragraph: the product in one sentence; the phase rule — *each phase adds one capability on the previous phase's components and must not pull forward components the next phase owns*; the **fixed stack** (what is not up for decision); where everything else is decided (§2.0).
2. Phase table: `Phase | Adds (architecture increment) | Must not need yet | Gate to next (PRD §Scope)`. One row per PRD phase. *Must not need yet* names components owned by later phases so a reviewer can catch pull-forward. *Gate* is a number: a count, a rate, a threshold, copied from the PRD's metrics or derived from them.
3. Out-of-scope paragraph: what the PRD excludes, and how any UI screens that look like exclusions are reconciled (a mobile screen is responsive web, not an app).
4. The traceability rule, verbatim: *Traceability rule for this document: every section names the PRD capability, non-functional row or screen it serves. A section that only restates the PRD is deleted.*

Pass: every phase row has a numeric gate; *Must not need yet* is non-empty for every phase except the last; the fixed stack is named in the paragraph.

## §2 C4 diagrams

Purpose: fix the pieces and their boundaries. Diagrams draw picks, not categories, so the decision table comes first.

Intro sentence: count the top-level pieces (*One web application, one database, one gateway, one workflow engine, one sandbox pool.*). This sentence is the architecture's budget: every container in §2.2 is one of these.

### 2.0 Component decisions (PRD §Architecture)

Table: `Component | Candidates | Pick | Why (≤ 5 lines) | Source`. One row per component outside the fixed stack. *Candidates* lists at least two options separated by ` · `. *Why* names the constraint that decided it (residency, a phase gate, a budget) and the rejected candidate's disqualifier in one clause. *Source* is the design reference the pick implements — a book chapter, an ADR, a standard, a vendor document — or `—`.

### 2.1 System context (PRD §Users and personas, §Architecture)

Mermaid `C4Context`. One `Person` per PRD persona; one `System` for the product; one `System_Ext` per external the product talks to (source-of-truth repository, model providers, identity provider, CI, mail, payment). `Rel` labels are verbs. Then at most three sentences stating boundary invariants: what is only ever authored where; what is never called directly.

### 2.2 Containers (PRD §Architecture, §Deployment)

Mermaid `C4Container` with a `System_Boundary` named with the region. One `Container` per piece counted in the intro. Then at most three sentences: which container users reach; which holds credentials; what isolated pools can reach.

### 2.3 Components per capability

Table: `Capability | Components | PRD "must have" it carries | Screen`. One row per PRD capability. *Components* are named modules (resolver, sensor, grader, router, meter), not categories. *Screen* lists the UI-package screen IDs the capability renders. Then a `flowchart` of the capability with the most branching, and one paragraph naming the invariant it protects (*sensors run before any judgment; a tier-G item never reaches a model*).

### 2.4 Deployment (PRD §Deployment, §Non-functional · Privacy)

Mermaid `flowchart TB` with nested `subgraph`s: region / residency boundary → tiers (web, control plane, data, isolated pools). A region the PRD mentions but does not ship is drawn as a subgraph containing `disabled`. Then: the tenancy model (row-level, policy, or deployment isolation) and which pool has no route to the data tier.

Pass: every container in §2.2 appears in §2.4; every component in §2.3 lives in a container from §2.2; every pick in §2.0 appears in §2.2 or §2.4; every screen in the UI package appears in some §2.3 row.

## §3 Network topology

Purpose: every byte path, with its port and its auth, and the default stance for anything not listed.

Intro: zone count, the default stance (*sandbox egress default-deny*), what can never reach what, with the PRD anchor. Then a `flowchart LR` where every edge label carries port and auth (`443`, `5432 mTLS`, `443 webhook + HMAC`).

### 3.1 Conduits

Table: `From | To | Protocol · port | Direction | Auth | Notes`. Every edge in the diagram is a row. Every isolated zone gets a deny-all row (`Sandbox | anything else | any | out | — | Denied at the host nftables; denial logged with session id`).

### 3.2 The riskiest path

The one path most likely to be attacked — egress from untrusted code, an inbound webhook, a file upload — drawn as its own `flowchart` down to the enforcement point (nftables rule, WAF rule, signature check) and the place a denial surfaces to a person (status bar, alert). Rename the heading to the path (*3.2 Sandbox egress path*).

### 3.3 Residency boundary

What runs in-region; what is outside by nature (model providers) and what crosses the boundary (prompts and completions, stored neither side); which admin-visible option is disabled until a second deployment exists.

### 3.4 Secrets and the model-visible surface

Table: `Secret | Lives in | Reachable by | Model-visible`. Every credential class, including user-supplied keys and signed URLs. Then a paragraph starting `Proof:` — how the "No" column is enforced mechanically: which fields each model-backed component receives (point at §8), that no environment, header or config object is serialised into a prompt, and the scanner that runs in CI and at log ingestion with its required count.

Pass: every conduit has a port and an auth value; every *Model-visible* cell is `No` or explains the exception.

## §4 Data model

Purpose: the schema the code will be generated from, and the PRD rules the schema itself enforces.

Intro: one datastore sentence; three to five domains named; the immutability rule (what is never updated in place; a new version is inserted instead).

### 4.1 Entity–relationship diagram (PRD §Capability …)

Mermaid `erDiagram`; relationship labels are verbs. Then one paragraph: the reading order across domains and the one entity that bridges two of them.

### 4.2 Schema

The real schema in the stack's language (Prisma, SQL DDL, SQLAlchemy, Drizzle) grouped by domain with `// ----- domain -----` comments, enums before models, a one-line comment on any field that encodes a PRD rule. Then: `Rules the schema enforces, with the PRD line each serves:` and a table `Rule | Mechanism`. *Mechanism* names the constraint, field, computed expression, or workflow refusal — a rule enforced "by convention" is not a mechanism.

### 4.3 Integrity specification

Present when the PRD has an auditability requirement. Bullets: canonical form (name the standard), hash algorithm and encoding, genesis value, chain scope (one chain; views are filters), what each record kind covers, the verification procedure, the export format with a signed trailer. Otherwise rename to the integrity mechanism the product does have (idempotency keys, event sourcing) or write one line stating none is required and why.

### 4.4 Retention and deletion (PRD §Non-functional · Privacy)

Table: `Data | Retention | Mechanism`. Every personal, sensitive, or regulated data class, plus ephemeral environments and user-supplied secrets. *Mechanism* names the job and the field it nulls or the row it deletes; *Retention* is a duration or `Never deleted` with the reason in *Mechanism*.

### 4.5 Ingestion / content pipeline

Present when content or data enters from a source of truth outside the product. `flowchart LR` from the source to published rows with the hash or validation gate. Bullets: idempotency key; migration policy (forward-only, one per PR, migration ships before content); seeding for development; the flow-back path when the product changes the source.

Pass: every entity in §4.1 has a model in §4.2; every rule's *Mechanism* names a field, constraint, or refusal; no retention row is `indefinite` without a reason.

## §5 Front end

Purpose: every screen the UI package defines maps to one route, one rendering mode, one auth rule.

Intro: the **spine** sentence (what the app is organised around; the other capabilities are routes or slots beside it, not separate apps) and *every screen in the UI package maps to one route below*.

### 5.1 Route map

Table: `Route | Screen (UI package) | Rendering | Auth`. One row per route; API routes in one row pointing to §6. Then the responsive rule: which routes render on small viewports and what the rest return.

### 5.2 Component tree and data fetching

Table: `Layer | Server components | Client components`. Then bullets, one mechanism each: cache keying and invalidation; pre-rendering (what is rendered once and where); streaming transport per channel with the rejected alternative's reason; i18n with the overflow check in CI; accessibility per component; keyboard map.

### 5.3 State

Table: `State | Lives in`. Rows for URL, server cache, database via actions, client memory, local storage (best effort).

### 5.4 Performance budgets (PRD §Non-functional · Performance)

Table: `Budget | Mechanism`. One row per PRD performance requirement. *Budget* carries the number; *Mechanism* says how it is met (pre-render, index type, warm pool, prompt-prefix caching).

Pass: every screen ID in the UI package appears in §5.1; every budget has a number and a mechanism.

## §6 Back end

Purpose: the contract. Every endpoint with its auth, limits and errors; the policy gate every call passes.

Intro: API style and where the contract is generated from; where long-running work goes; the base path; the auth and policy gate every endpoint passes before touching data.

### 6.1 Endpoint catalogue

Table: `Method · path | Auth · role | Request → response | Rate limit | Idempotency | Errors`. Every endpoint, webhooks included; streaming endpoints marked `(SSE)` or `WS`. Escape `|` inside a cell as `\|`. Then the error-body convention in one sentence.

### 6.2 Authorisation model

`flowchart LR` of the decision point with the `unreachable → deny` edge drawn. Table: `Subject | May`, one row per role plus one per service or agent identity (what it may read, what it may write, what it may never read). Then: which rules are policy rather than application code, where policy is versioned, and what a failed policy load does (keep last good bundle, alert).

### 6.3 Budget / cost enforcement

Present when the product meters model calls, compute minutes or any priced resource. Bullets: where the cap is enforced (before the call, at the gateway, never counted in application code); who receives no key; how the meter writes and which screens read it; what happens at the cap, per capability.

### 6.4 Rate limits and the throttle rule

Table: `Rule | Value | Enforced at`. Includes abuse rules with their thresholds and consequences.

Pass: every endpoint has an auth role and an error list (`—` when none); every limit has a value and an enforcement point.

## §7 Sequence diagrams

Purpose: the runtime truth of each capability including how it fails.

Intro: count the flows; name the loop pattern (plan · act · observe · verify · repair) and the cap discipline; name where sensors sit relative to judgment.

One `sequenceDiagram` per primary flow: at least one per PRD capability, plus override/escalation, release/merge, and one for integrations (SSO, metering, signals, export). Each has `autonumber`, participants named by role, at least one `alt` failure branch, `par` for concurrent watchdogs, and a cap on every retry or repair (`one repair pass (cap 1)`).

After each diagram, one paragraph: the invariant the diagram protects and what a user never sees.

Pass: every diagram has an `alt`; every retry names its cap; every flow writes to the audit record where one exists.

## §8 AI agent specifications

Present when any component calls a model. Otherwise one line — *No model-backed components in this release.* — and the numbering stays.

Intro: count the agents; each has a versioned guide with a byte-stable prefix, a structured output schema, sensors on both sides, and a calibration procedure.

Comparison table, one column per agent, rows in this order: `Model tier`, `Guide` (versioned path), `Prefix order (byte-stable, cached)`, `May read`, `May never read`, `Output schema`, `Sensors before`, `Sensors after`, `Cap`. Then a paragraph: where guides live, how a guide edit ships, what each prompt logs (guide version, model id).

### 8.1 Calibration (PRD §Metrics)

Table: `Agent | Reference set | Metric | Gate | Retirement`. The seeded-item rule if the product seeds human queues. The current reading if one exists.

Pass: every agent's *May never read* includes user identity unless the row justifies otherwise; every score, threshold or arithmetic the agent produces is recomputed in code (`Sensors after`).

## §9 Observability and audit

Intro: the conventions used (OTel GenAI semantic conventions on every model call) and what goes to the audit record, with the PRD anchor.

Table: `Event | Span attributes | Stored in`. Then `Dashboards, one per PRD headline metric and one for leading indicators:` with table `Dashboard | Series`. Then `Not collected, by design (PRD §What is not measured):` naming what is deliberately absent and the structural reason (no leaderboard query exists). Then the audit export in one sentence pointing at §4.3.

## §10 Security and threat model

Intro: count the attacks the PRD names, with the PRD anchor.

Table: `Attack | Control | Source | Detection | Residual risk`. *Residual risk* is never empty — a control with no residual is a control nobody examined. Then the fail-closed paragraph: every decision point (policy, gateway, orchestrator, webhook signature) and its behaviour when unreachable or invalid.

## §11 Testing, CI/CD and environments

Intro: the regression gate in one sentence.

Table: `Level | What | Tooling | Gate`. Levels: unit (the arithmetic and routing rules, with the PRD's worked examples as fixtures), contract, policy, integration, end to end (every screen's primary flow, accessibility standard), golden sets (the phase gates), the domain suite, load (against §5.4 budgets). Then environments and the promotion rule (what promotes by tag, what by merge, canary share and duration). Then the release procedure as an arrow chain and rollback for content, code and migrations separately.

## §12 Open decisions and assumptions

Intro: *The PRD's open questions, with the assumption this TRD builds on until they are decided.*

Table: `Question (PRD §Open questions) | Assumption used here | What changes if decided otherwise`. One row per PRD open question; *What changes* names the schema, container or policy that moves. Then a closing paragraph starting `Decisions this document made that the PRD left open, for review:` listing each decision with its section number in parentheses.

Pass: every PRD open question has a row; every decision the TRD made on its own appears in the closing list with a section reference.

---

## Cross-section tests

Run after the draft, before lint:

- **Restatement.** For each section ask: does it add a mechanism, a number, a boundary or a decision the PRD does not contain? A section that only restates the PRD is deleted (the §1 rule).
- **Anchor.** Every H3 heading carries its PRD anchor in parentheses (`(PRD §Capability 2)`, `(PRD §Non-functional · Privacy)`) or the body cites one in its first paragraph. A section with no anchor is tracing to nothing.
- **Number.** Every budget, limit, retention, threshold and gate is a number. A limit without a value is a wish.
- **Candidate.** Every pick in §2.0 had an alternative with a stated disqualifier.
- **Mechanism.** Every rule in §4.2's table, every budget in §5.4, every control in §10 names the thing that enforces it.
- **Closure.** Every unknown became a §12 row with an assumption. The strings `TBD`, `TODO`, `TBC`, `to be defined` and `to be decided` do not appear.
- **Coverage.** Every PRD capability, non-functional row, screen ID and open question is cited at least once. Keep the traceability ledger from the workflow's step 2 and tick each entry; an unticked entry is either a missing section or a PRD line the TRD should say it does not serve, and why.
