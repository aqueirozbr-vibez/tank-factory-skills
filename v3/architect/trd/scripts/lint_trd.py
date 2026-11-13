#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""TRD lint for docs/trd/<product>.md (Tank Factory v3 shape).

Usage: python3 lint_trd.py docs/trd/<product>.md [--prd docs/prd/<product>.md]
           [--research docs/research/<brief>.md] [--mode new|amendment|as-built]

Checks the fifteen numbered sections, the eleven TRD building blocks (DevOps,
C4, stack, network topology, endpoint map, component map, integration
sequences, MER, data flow, AI orchestration, MLOps), that every endpoint is
typed and that every invariant names a check under evals/tech/. The stack
profile block itself is validated by the stack_profile skill's lint.
Exit 1 on any FAIL.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

TITLES = ["Purpose, scope, phases", "Stack", "C4 diagrams", "Component map", "Network topology",
          "Data model (MER)", "Data flow", "Endpoint map", "Integration sequences",
          "AI orchestration and protocols", "MLOps", "DevOps", "Security and threat model",
          "Testing", "Open decisions and assumptions"]
METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "WS", "SSE"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower()).rstrip("s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--prd")
    ap.add_argument("--research")
    ap.add_argument("--mode", default=None, choices=["new", "amendment", "as-built"])
    a = ap.parse_args()
    text = md.read(a.path)
    rep = md.Report("TRD lint")
    lines = text.splitlines()
    head = "\n".join(lines[:5])
    mode = a.mode or (re.search(r"mode\s+(new|amendment|as-built)", head) or [None, "new"])[1]

    if not lines or not re.match(r"^#\s+TRD\s+[—-]\s+\S", lines[0]):
        rep.fail("H1 must be '# TRD — <Product name>' on line 1")
    if not re.search(r"\b(19|20)\d{2}\b", head) or not re.search(r"\bv\d+\.\d+", head):
        rep.fail("byline must carry a date and a version")
    if not re.search(r"traces to PRD\s+v\d+\.\d+", head):
        rep.fail("byline must say 'traces to PRD v<x.y>'")

    secs = md.sections(text)
    S = {}
    for i, t in enumerate(TITLES, 1):
        want = f"{i}. {t}"
        if want not in dict(secs):
            rep.fail(f"missing section '## {want}' (exact text; it is an anchor)")
        else:
            S[i] = dict(secs)[want]
    order = [t for t, _ in secs if re.match(r"^\d+\.\s", t)]
    if order != sorted(order, key=lambda t: int(t.split(".")[0])):
        rep.fail("numbered sections are out of order")
    for i in range(2, 15):
        if i in S:
            serves = md.labelled(S[i], "Serves")
            if not serves or not re.search(r"PRD\s+§|FR-\d|SC-\d", serves):
                rep.fail(f"§{i}: no 'Serves:' line naming the PRD anchors it traces to")

    prd_objects, prd_fr, prd_personas, prd_nfr = [], set(), [], ""
    if a.prd:
        prd = md.read(a.prd)
        oh, orows = md.table(md.section(prd, "Objects") or "", ["Object", "Definition"])
        prd_objects = [r[0].strip("*` ") for r in orows]
        prd_fr = set(re.findall(r"^\s*[-*]\s+(FR-\d+\.\d+)\s*:", prd, re.M))
        ph, prows = md.table(md.section(prd, "Users and personas") or "", ["Persona", "Who"])
        prd_personas = [r[0].strip("*` ") for r in prows]
        prd_nfr = md.section(prd, "Non-functional requirements") or ""

    # §1
    if 1 in S:
        hdr, rows = md.table(S[1], ["Phase", "Adds", "Gate"])
        if hdr is None or not rows:
            rep.fail("§1: phase table missing (Phase | Adds | Gate)")
        for r in rows:
            if not md.has_number(md.cell(r, hdr, "Gate")):
                rep.fail(f"§1: phase '{r[0][:30]}' gate has no number")
        if "traceability rule" not in S[1].lower():
            rep.fail("§1: the traceability rule sentence is missing")

    # §2
    if 2 in S:
        if md.table(S[2], ["Choice", "Pick", "Alternatives", "Why"])[0] is None:
            rep.fail("§2: decisions table missing (Choice | Pick | Alternatives | Why)")
        m = re.search(r"```json\s+stack_profile\s*\n(.*?)\n```", S[2], re.S)
        if not m:
            rep.fail("§2: no ```json stack_profile block")
        else:
            try:
                json.loads(m.group(1))
            except ValueError as exc:
                rep.fail(f"§2: stack_profile block is not valid JSON: {exc}")
        if md.labelled(S[2], "Guardrail requests") is None:
            rep.fail("§2: 'Guardrail requests:' line missing (write 'none' when there are none)")

    # §3
    if 3 in S:
        ctx, cont = md.mermaid(S[3], "C4Context"), md.mermaid(S[3], "C4Container")
        comp = md.mermaid(S[3], "C4Component") + md.mermaid(S[3], "flowchart")
        if not ctx:
            rep.fail("§3.1: Mermaid C4Context diagram missing")
        if not cont:
            rep.fail("§3.2: Mermaid C4Container diagram missing")
        if not comp:
            rep.fail("§3.3: component diagram missing (C4Component or flowchart)")
        for p in prd_personas:
            if ctx and p not in ctx[0]:
                rep.fail(f"§3.1: persona '{p}' is not in the system context, named as the PRD names it")
        for d in ctx + cont:
            for rel in re.findall(r"Rel\w*\(([^)]*)\)", d):
                if rel.count(",") < 2:
                    rep.fail(f"§3: relation without a label: Rel({rel[:50]})")

    # §4
    folders, inv_ids = [], []
    if 4 in S:
        hdr, rows = md.table(S[4], ["Component", "Repository", "Folder", "Responsibility", "May import", "Never imports"])
        if hdr is None or not rows:
            rep.fail("§4: component map missing (Component | Repository | Folder | Responsibility | May import | Never imports)")
        for r in rows:
            f = re.findall(r"`([^`]+)`", md.cell(r, hdr, "Folder"))
            if not f:
                rep.fail(f"§4: component '{r[0]}' names no folder in backticks")
            folders += f
            if md.is_empty(md.cell(r, hdr, "Responsibility")):
                rep.fail(f"§4: component '{r[0]}' has no responsibility")
            if mode == "as-built" and md.col(hdr, "Code") < 0:
                rep.fail("§4: as-built component map needs a 'Code' column")
                break
        ih, irows = md.table(md.section(S[4], "4.1 Invariants", 3) or "", ["ID", "Invariant", "Check", "Serves"])
        if ih is None:
            rep.fail("§4.1: invariants table missing (ID | Invariant | Check | Serves)")
        elif len(irows) < 4:
            rep.fail(f"§4.1: {len(irows)} invariants; the context gate needs ≥ 4")
        for r in irows:
            iid = r[0].strip("*` ")
            inv_ids.append(iid)
            if not re.match(r"^INV-\d+$", iid):
                rep.fail(f"§4.1: invariant id '{iid}' must be INV-<n>")
            if not re.search(r"`evals/tech/[^`]+`", md.cell(r, ih, "Check")):
                rep.fail(f"§4.1: {iid} names no check file under evals/tech/")
            if md.is_empty(md.cell(r, ih, "Serves")):
                rep.fail(f"§4.1: {iid} serves no PRD line")

    # §5
    if 5 in S:
        if not md.mermaid(S[5], "flowchart") and not md.mermaid(S[5], "graph"):
            rep.fail("§5: Mermaid flowchart of the network missing")
        hdr, rows = md.table(S[5], ["From", "To", "Protocol", "Auth"])
        if hdr is None or not rows:
            rep.fail("§5: conduits table missing (From | To | Protocol · port | Auth | Notes)")
        for r in rows:
            proto = md.cell(r, hdr, "Protocol")
            if not re.search(r"\d|any", proto):
                rep.fail(f"§5: conduit {r[0]} → {r[1]} has no port")
            if md.is_empty(md.cell(r, hdr, "Auth")) and "any" not in proto:
                rep.fail(f"§5: conduit {r[0]} → {r[1]} has no auth")
        if not any("den" in " ".join(r).lower() for r in rows):
            rep.warn("§5: no deny-by-default row in the conduits table")

    # §6
    if 6 in S:
        er = md.mermaid(S[6], "erDiagram")
        if not er:
            rep.fail("§6: Mermaid erDiagram missing")
        else:
            for ent, body in re.findall(r"^\s*([A-Za-z_][\w-]*)\s*\{([^}]*)\}", er[0], re.M):
                for attr in [x.strip() for x in body.splitlines() if x.strip()]:
                    if len(attr.split()) < 2:
                        rep.fail(f"§6: entity {ent} attribute '{attr}' has no type")
            if not re.search(r"\|\|--|\}o--|\|o--|--o\{|--\|\{|--\|\|", er[0]):
                rep.fail("§6: erDiagram shows no relationship with cardinality")
        hdr, rows = md.table(S[6], ["Entity", "PRD object", "Keys", "Retention"])
        if hdr is None or not rows:
            rep.fail("§6: entity table missing (Entity | PRD object | Keys | Indexes | Retention)")
        else:
            mapped = {norm(md.cell(r, hdr, "PRD object")) for r in rows}
            for o in prd_objects:
                if norm(o) not in mapped:
                    rep.fail(f"§6: PRD object '{o}' has no entity")
            for r in rows:
                if er and norm(r[0]) not in {norm(e) for e in re.findall(r"^\s*([A-Za-z_][\w-]*)\s*\{", er[0], re.M)}:
                    rep.fail(f"§6: entity '{r[0]}' is in the table but not in the erDiagram")
            if mode == "as-built" and md.col(hdr, "Code") < 0:
                rep.fail("§6: as-built entity table needs a 'Code' column")

    # §7
    if 7 in S:
        hdr, rows = md.table(S[7], ["Object", "Created", "Stored", "Sent to", "Deleted", "Personal data"])
        if hdr is None or not rows:
            rep.fail("§7: data-flow table missing (Object | Created | Stored | Sent to | Deleted | Personal data)")
        else:
            have = {norm(r[0]) for r in rows}
            for o in prd_objects:
                if norm(o) not in have:
                    rep.fail(f"§7: PRD object '{o}' has no data-flow row")
            for r in rows:
                pd = md.cell(r, hdr, "Personal data").strip().lower()
                if pd not in {"yes", "no"}:
                    rep.fail(f"§7: '{r[0]}' personal data must be yes or no")
                if pd == "yes" and md.is_empty(md.cell(r, hdr, "Deleted")):
                    rep.fail(f"§7: '{r[0]}' holds personal data and has no deletion path")

    # §8
    cited_fr = set(re.findall(r"FR-\d+\.\d+", text))
    if 8 in S:
        hdr, rows = md.table(S[8], ["Method", "Path", "Roles", "Request", "Response", "Errors", "Idempotency", "Rate limit", "Serves"])
        if hdr is None or not rows:
            rep.fail("§8: endpoint map missing (Method | Path | Roles | Request | Response | Errors | Idempotency | Rate limit | Serves)")
        types_src = "\n".join(b for _, b in md.code_blocks(md.section(S[8], "8.1 Types", 3) or ""))
        defined = set(re.findall(r"\b(?:type|interface|class|enum|message)\s+([A-Z]\w*)", types_src))
        defined |= set(re.findall(r'"(?:title|\$id)"\s*:\s*"([A-Z]\w*)"', types_src))
        if rows and not defined:
            rep.fail("§8.1: no types defined in a code block; an endpoint is typed only when its types are written out")
        for r in rows:
            ep = f"{md.cell(r, hdr, 'Method')} {md.cell(r, hdr, 'Path')}"
            if md.cell(r, hdr, "Method").strip("` ").upper() not in METHODS:
                rep.fail(f"§8: '{ep}' has an unknown method")
            if not md.cell(r, hdr, "Path").strip("` ").startswith("/"):
                rep.fail(f"§8: '{ep}' path must start with /")
            for c in ("Request", "Response"):
                v = md.cell(r, hdr, c)
                names = re.findall(r"`([A-Z]\w*)(?:\[\])?`", v)
                if not names:
                    if c == "Response" or not md.is_empty(v):
                        rep.fail(f"§8: '{ep}' {c.lower()} names no type — every endpoint is typed")
                for n in names:
                    if n not in defined:
                        rep.fail(f"§8: '{ep}' {c.lower()} type `{n}` is not defined in §8.1")
            for c in ("Roles", "Errors", "Idempotency", "Rate limit"):
                if md.is_empty(md.cell(r, hdr, c)):
                    rep.fail(f"§8: '{ep}' has no {c.lower()}")
            fr = re.findall(r"FR-\d+\.\d+", md.cell(r, hdr, "Serves"))
            if not fr:
                rep.fail(f"§8: '{ep}' serves no FR id")
            for x in fr:
                if prd_fr and x not in prd_fr:
                    rep.fail(f"§8: '{ep}' serves {x}, which the PRD does not define")
            if mode == "as-built" and md.col(hdr, "Code") < 0:
                rep.fail("§8: as-built endpoint map needs a 'Code' column")
                break

    # §9
    if 9 in S:
        hdr, rows = md.table(S[9], ["Integration", "System", "Direction", "Auth", "Timeout", "Retries"])
        none9 = md.labelled(S[9], "None")
        seqs = md.mermaid(S[9], "sequenceDiagram")
        if hdr is None and not none9:
            rep.fail("§9: integrations table missing (Integration | System | Direction | Auth | Timeout | Retries), or write 'None: <reason>'")
        if len(seqs) < len(rows):
            rep.fail(f"§9: {len(rows)} integrations but {len(seqs)} sequence diagrams; draw one per integration")
        for i, s in enumerate(seqs, 1):
            if not re.search(r"^\s*alt\b", s, re.M):
                rep.fail(f"§9: sequence diagram {i} has no 'alt' failure branch")
        for r in rows:
            if not re.search(r"\d", md.cell(r, hdr, "Timeout")):
                rep.fail(f"§9: integration '{r[0]}' timeout has no number")
        if a.research and hdr:
            res = md.read(a.research)
            bh, brows = md.table(md.section(res, "Customer blueprint") or "", ["Step", "Support system"])
            systems = " ".join(md.cell(r, hdr, "System") for r in rows)
            for sysname in sorted({md.cell(r, bh, "Support system").strip("*` ") for r in brows}):
                if sysname and not md.is_empty(sysname) and sysname not in systems:
                    rep.fail(f"§9: support system '{sysname}' from the research blueprint has no integration")

    # §10, §11
    calls = []
    if 10 in S:
        if md.labelled(S[10], "None") is None:
            hdr, rows = md.table(S[10], ["Call", "Model tier", "Prompt", "May read", "May never read", "Tools",
                                         "Output schema", "Checks before", "Checks after", "Cap"])
            if hdr is None or not rows:
                rep.fail("§10: calls table missing (Call | Model tier | Prompt | May read | May never read | Tools | "
                         "Output schema | Checks before | Checks after | Cap), or write 'None: <reason>'")
            for r in rows:
                calls.append(r[0].strip("*` "))
                for c in ("Model tier", "Prompt", "May read", "May never read", "Output schema", "Checks after"):
                    if md.is_empty(md.cell(r, hdr, c)):
                        rep.fail(f"§10: call '{r[0]}' has no {c.lower()}")
                if not re.search(r"\d", md.cell(r, hdr, "Cap")):
                    rep.fail(f"§10: call '{r[0]}' cap has no number")
            if md.table(S[10], ["Protocol", "Used for", "Auth"])[0] is None:
                rep.fail("§10: protocols table missing (Protocol | Used for | Auth)")
    if 11 in S:
        if md.labelled(S[11], "None") is None:
            hdr, rows = md.table(S[11], ["Call", "Reference set", "Metric", "Gate", "Cadence", "Drift monitor", "Retirement"])
            if hdr is None or not rows:
                rep.fail("§11: table missing (Call | Reference set | Metric | Gate | Cadence | Drift monitor | Retirement), or write 'None: <reason>'")
            have = {r[0].strip("*` ") for r in rows}
            for c in calls:
                if c not in have:
                    rep.fail(f"§11: model call '{c}' from §10 has no eval row")
            for r in rows:
                if not re.search(r"\d", md.cell(r, hdr, "Gate")):
                    rep.fail(f"§11: '{r[0]}' gate has no number")
                for c in ("Reference set", "Metric", "Drift monitor", "Retirement"):
                    if md.is_empty(md.cell(r, hdr, c)):
                        rep.fail(f"§11: '{r[0]}' has no {c.lower()}")
            if md.labelled(S[11], "Versioning") is None:
                rep.fail("§11: 'Versioning:' line missing")
        elif calls:
            rep.fail("§11 says None but §10 lists model calls")

    # §12
    if 12 in S:
        if md.table(S[12], ["Environment", "Purpose", "Deploys from", "Data"])[0] is None:
            rep.fail("§12: environments table missing (Environment | Purpose | Deploys from | Data)")
        if md.labelled(S[12], "Pipeline") is None:
            rep.fail("§12: 'Pipeline:' line missing")
        rb = md.labelled(S[12], "Rollback")
        if not rb or not re.search(r"\d", rb):
            rep.fail("§12: 'Rollback:' line missing or without a time")
        hdr, rows = md.table(S[12], ["SLO", "Alert", "Threshold"])
        if hdr is None or not rows:
            rep.fail("§12: SLO alerts table missing (SLO | Alert | Threshold)")
        for r in rows:
            if not re.search(r"\d", md.cell(r, hdr, "Threshold")):
                rep.fail(f"§12: alert '{r[0][:30]}' threshold has no number")
        if prd_nfr and rows and not any("availab" in r[0].lower() for r in rows):
            rep.warn("§12: no alert for the PRD's Availability row")

    # §13–§15
    if 13 in S:
        hdr, rows = md.table(S[13], ["Threat", "Path", "Control", "Check"])
        if hdr is None or not rows:
            rep.fail("§13: threat table missing (Threat | Path | Control | Check)")
        for r in rows:
            if md.is_empty(md.cell(r, hdr, "Control")):
                rep.fail(f"§13: threat '{r[0][:30]}' has no control")
        if md.table(S[13], ["Secret", "Lives in", "Reachable by"])[0] is None:
            rep.fail("§13: secrets table missing (Secret | Lives in | Reachable by)")
    if 14 in S:
        if md.table(S[14], ["Layer", "What", "Where", "Runs"])[0] is None:
            rep.fail("§14: testing table missing (Layer | What | Where | Runs)")
        if "evals/tech" not in S[14]:
            rep.fail("§14: the conformance checks under evals/tech/ are not listed")
    if 15 in S:
        hdr, rows = md.table(S[15], ["Decision", "Options", "Assumed", "Owner", "Needed by"])
        if hdr is None:
            rep.fail("§15: table missing (Decision | Options | Assumed | Owner | Needed by)")
        for r in rows:
            if md.is_empty(md.cell(r, hdr, "Assumed")):
                rep.fail(f"§15: decision '{r[0][:30]}' has no assumed option")

    for x in sorted(prd_fr - cited_fr, key=lambda s: [int(n) for n in re.findall(r"\d+", s)]):
        rep.warn(f"{x} is cited nowhere in the TRD; confirm no component serves it")

    md.check_placeholders(text, rep, "TRD")
    rep.finish()


if __name__ == "__main__":
    main()
