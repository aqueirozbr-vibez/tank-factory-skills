#!/usr/bin/env python3
"""Deterministic checks on a TRD markdown file.

Usage: python3 scripts/lint_trd.py path/to/trd.md [--no-agents]

Checks structure (12 sections in order), required table columns, required
diagram kinds, failure branches and caps in sequence diagrams, PRD anchors on
subsections, closure (no TBD/TODO), and the §12 review list.

Exit 1 on any FAIL. WARN lines never fail the run.
--no-agents: skip the §8 agent-table checks (product has no model-backed components).
"""
import re
import sys

SECTIONS = [
    (1, r"purpose"),
    (2, r"c4"),
    (3, r"network"),
    (4, r"data model"),
    (5, r"front end|frontend"),
    (6, r"back end|backend"),
    (7, r"sequence"),
    (8, r"agent"),
    (9, r"observab"),
    (10, r"security|threat"),
    (11, r"testing|ci/cd"),
    (12, r"open decisions|assumptions"),
]

# section number -> list of (table label, required header cells)
REQUIRED_TABLES = {
    1: [("phase table", ["Phase", "Adds", "Must not need yet", "Gate"])],
    2: [("component decisions", ["Component", "Candidates", "Pick", "Why", "Source|Chapter|Reference"]),
        ("components per capability", ["Capability", "Components", "must have", "Screen"])],
    3: [("conduits", ["From", "To", "Protocol", "Direction", "Auth", "Notes"]),
        ("secrets", ["Secret", "Lives in", "Reachable by", "Model-visible"])],
    4: [("schema rules", ["Rule", "Mechanism"]),
        ("retention", ["Data", "Retention", "Mechanism"])],
    5: [("route map", ["Route", "Screen", "Rendering", "Auth"]),
        ("component tree", ["Layer", "Server components", "Client components"]),
        ("state", ["State", "Lives in"]),
        ("performance budgets", ["Budget", "Mechanism"])],
    6: [("endpoint catalogue", ["Method", "Auth", "Request", "Rate limit", "Idempotency", "Errors"]),
        ("authorisation", ["Subject", "May"]),
        ("rate limits", ["Rule", "Value", "Enforced at"])],
    8: [("agent table", ["Model tier", "Guide", "Prefix order", "May read", "May never read",
                         "Output schema", "Sensors before", "Sensors after", "Cap"]),
        ("calibration", ["Agent", "Reference set", "Metric", "Gate", "Retirement"])],
    9: [("events", ["Event", "Span attributes", "Stored in"]),
        ("dashboards", ["Dashboard", "Series"])],
    10: [("threat model", ["Attack", "Control", "Source|Chapter|Reference", "Detection", "Residual risk"])],
    11: [("test levels", ["Level", "What", "Tooling", "Gate"])],
    12: [("open questions", ["Question", "Assumption", "What changes"])],
}

# section number -> required mermaid diagram kinds (first token of the block)
REQUIRED_DIAGRAMS = {
    2: ["C4Context", "C4Container", "flowchart"],
    3: ["flowchart"],
    4: ["erDiagram"],
    6: ["flowchart"],
    7: ["sequenceDiagram"],
}

FORBIDDEN = [r"\bTBD\b", r"\bTODO\b", r"\bTBC\b", r"to be defined", r"to be decided", r"\bFIXME\b"]

ANCHOR_RE = re.compile(r"\((?:PRD\s*§|§|ch\d|ADR|RFC|[A-Z]{2,5}-\d)", re.I)


def split_sections(lines):
    """Return {section_number: (title, [lines])} for H2 headings of the form '## N. Title'."""
    out, cur, buf, title = {}, None, [], None
    for ln in lines:
        m = re.match(r"^##\s+(\d{1,2})\.\s+(.*)$", ln)
        if m:
            if cur is not None:
                out[cur] = (title, buf)
            cur, title, buf = int(m.group(1)), m.group(2).strip(), []
        elif cur is not None:
            buf.append(ln)
    if cur is not None:
        out[cur] = (title, buf)
    return out


def tables(lines):
    """Yield header-cell lists for every markdown table (header row followed by a --- row)."""
    for i in range(len(lines) - 1):
        if lines[i].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[i + 1]):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            yield cells


def agent_table_rows(lines):
    """Row labels (first cell) of tables whose header starts with an empty cell."""
    labels = []
    for i in range(len(lines) - 1):
        if lines[i].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if header and header[0] == "":
                j = i + 2
                while j < len(lines) and lines[j].startswith("|"):
                    labels.append(lines[j].strip().strip("|").split("|")[0].strip())
                    j += 1
    return labels


def mermaid_blocks(lines):
    blocks, cur = [], None
    for ln in lines:
        if ln.strip().startswith("```mermaid"):
            cur = []
        elif cur is not None and ln.strip().startswith("```"):
            blocks.append(cur)
            cur = None
        elif cur is not None:
            cur.append(ln)
    return blocks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_agents = "--no-agents" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    text = open(args[0], encoding="utf-8").read()
    lines = text.splitlines()
    fails, warns = [], []

    # Header
    if not lines or not re.match(r"^#\s+TRD\s+[—-]\s+\S", lines[0]):
        fails.append("H1 must be '# TRD — <Product name>' on line 1")
    head = "\n".join(lines[:6])
    if "traces to PRD" not in head:
        fails.append("byline must say 'traces to PRD <id>' within the first lines")
    if not re.search(r"\bv\d+\.\d+", head):
        fails.append("byline must carry a version like v0.1")

    # Sections present, in order
    secs = split_sections(lines)
    for n, pat in SECTIONS:
        if n not in secs:
            fails.append(f"§{n} missing (expected a '## {n}. …' heading)")
        elif not re.search(pat, secs[n][0], re.I):
            warns.append(f"§{n} title '{secs[n][0]}' does not look like the expected section")
    nums = sorted(secs)
    if nums != list(range(1, len(nums) + 1)):
        fails.append(f"section numbering is not 1..N in order: {nums}")

    # Traceability rule
    if 1 in secs and "restates the PRD is deleted" not in "\n".join(secs[1][1]):
        fails.append("§1 must carry the traceability rule ('…only restates the PRD is deleted')")

    # Tables
    for n, reqs in REQUIRED_TABLES.items():
        if n not in secs:
            continue
        if n == 8 and no_agents:
            continue
        body = secs[n][1]
        headers = list(tables(body))
        for label, cols in reqs:
            if n == 8 and label == "agent table":
                labels = agent_table_rows(body)
                missing = [c for c in cols if not any(c.lower() in l.lower() for l in labels)]
                if labels == []:
                    fails.append("§8 agent comparison table missing (header starts with an empty cell)")
                elif missing:
                    fails.append(f"§8 agent table missing rows: {missing}")
                continue
            def has(col, hdr):
                return any(any(alt.lower() in h.lower() for h in hdr) for alt in col.split("|"))
            ok = any(all(has(c, hdr) for c in cols) for hdr in headers)
            if not ok:
                fails.append(f"§{n} {label} table missing or missing columns {cols}")

    # Diagrams
    for n, kinds in REQUIRED_DIAGRAMS.items():
        if n not in secs:
            continue
        blocks = mermaid_blocks(secs[n][1])
        firsts = [b[0].strip().split()[0] if b and b[0].strip() else "" for b in blocks]
        for k in kinds:
            if not any(f.startswith(k) for f in firsts):
                fails.append(f"§{n} needs a mermaid '{k}' diagram")

    # Sequence diagrams: alt branch, autonumber, caps
    if 7 in secs:
        for i, b in enumerate(mermaid_blocks(secs[7][1]), 1):
            txt = "\n".join(b)
            if "sequenceDiagram" not in txt:
                continue
            if "autonumber" not in txt:
                warns.append(f"§7 diagram {i}: add 'autonumber'")
            if not re.search(r"^\s*(alt|par)\b", txt, re.M):
                fails.append(f"§7 diagram {i}: no failure branch ('alt', or a 'par' watchdog)")
            if re.search(r"repair|retry|re-?run", txt, re.I) and not re.search(r"cap\s*\d|\(cap", txt, re.I):
                warns.append(f"§7 diagram {i}: a repair/retry without a stated cap")
        # every diagram followed by an invariant paragraph
        body = secs[7][1]
        for i in range(len(body) - 1):
            if body[i].strip() == "```" and i + 1 < len(body):
                nxt = next((l for l in body[i + 1:] if l.strip()), "")
                if nxt.startswith("#") or nxt.startswith("```"):
                    warns.append("§7: a diagram is not followed by its invariant paragraph")

    # Anchors: every section traces to the PRD. An H2's intro (text before its first H3)
    # covers its subsections; an H3 outside such a section carries its own anchor in the
    # heading or its first paragraph.
    for n, (title, body) in secs.items():
        if n == 12:
            continue
        first_h3 = next((i for i, l in enumerate(body) if l.startswith("### ")), len(body))
        intro = " ".join(body[:first_h3])
        intro_anchored = bool(re.search(r"PRD\s*§", intro))
        if not intro_anchored and first_h3 == len(body) and n not in (1,):
            warns.append(f"§{n} has no PRD anchor")
        if intro_anchored:
            continue
        for idx, ln in enumerate(body):
            if ln.startswith("### ") and not ANCHOR_RE.search(ln):
                para = " ".join(body[idx + 1: idx + 6])
                if not re.search(r"PRD\s*§", para):
                    warns.append(f"§{n} '{ln[4:60]}' has no PRD anchor in heading, first paragraph, or section intro")

    # §2.0 candidates: at least two per row
    if 2 in secs:
        body = secs[2][1]
        for i in range(len(body) - 1):
            if body[i].startswith("|") and "Candidates" in body[i]:
                j = i + 2
                while j < len(body) and body[j].startswith("|"):
                    cells = [c.strip() for c in body[j].strip().strip("|").split("|")]
                    if len(cells) >= 2 and "·" not in cells[1] and " or " not in cells[1].lower():
                        warns.append(f"§2.0 '{cells[0]}': only one candidate listed")
                    j += 1
                break

    # §3.1 deny-all row
    if 3 in secs and not re.search(r"anything else|everything else|default[- ]deny", "\n".join(secs[3][1]), re.I):
        warns.append("§3.1: no deny-all row for isolated zones")

    # §10 residual risk never empty
    if 10 in secs:
        body = secs[10][1]
        for i in range(len(body) - 1):
            if body[i].startswith("|") and "Residual risk" in body[i]:
                j = i + 2
                while j < len(body) and body[j].startswith("|"):
                    cells = [c.strip() for c in body[j].strip().strip("|").split("|")]
                    if len(cells) >= 5 and cells[4] in ("", "—", "-", "none", "None"):
                        fails.append(f"§10 '{cells[0][:40]}': residual risk is empty")
                    j += 1
                break
        if "fail-closed" not in "\n".join(body).lower():
            fails.append("§10 must contain the fail-closed paragraph")

    # §12 review list
    if 12 in secs and "Decisions this document made" not in "\n".join(secs[12][1]):
        fails.append("§12 must end with 'Decisions this document made that the PRD left open, for review: …'")

    # Closure
    for pat in FORBIDDEN:
        for m in re.finditer(pat, text, re.I):
            line_no = text[: m.start()].count("\n") + 1
            fails.append(f"line {line_no}: unresolved placeholder '{m.group(0)}' — make it a §12 row")

    # Template residue
    for m in re.finditer(r"<[A-Z][^<>\n]{3,80}>", text):
        if m.group(0).startswith(("<br", "<!--")):
            continue
        line_no = text[: m.start()].count("\n") + 1
        fails.append(f"line {line_no}: template placeholder left in: {m.group(0)[:50]}")

    for w in warns:
        print(f"WARN  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    print(f"\n{len(fails)} fail, {len(warns)} warn")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
