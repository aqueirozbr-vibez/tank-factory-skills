#!/usr/bin/env python3
"""Deterministic checks on a PRD markdown file.

Usage: python3 scripts/lint_prd.py path/to/prd.md

Checks the fixed section headings (the anchors a TRD cites), required table
columns, numeric targets and gates, capability sections with testable
requirements, instrument sections where judgments are made, boundaries
(non-goals, out of scope, what is not measured), open questions, and closure.

Exit 1 on any FAIL. WARN lines never fail the run.
"""
import re
import sys

FIXED_ORDER = [
    "Summary",
    "Problem and goals",
    "Users and personas",
    "Architecture",
    "Non-functional requirements",
    "Metrics and success criteria",
    "Scope, phases, and release plan",
    "Risks and open questions",
]

NFR_AREAS = ["Security", "Privacy", "Cost control", "Performance", "Availability",
             "Accessibility", "Languages", "Auditability", "Content integrity"]
NFR_REQUIRED = {"Security", "Privacy", "Performance", "Availability", "Auditability"}

TABLES = {
    "Summary": [("capability table", ["Capability", "What the user does", "guarantees"])],
    "Problem and goals": [("goals table", ["Goal", "Target", "Measure"])],
    "Users and personas": [("persona table", ["Persona", "Who", "Primary use", "Must have"])],
    "Architecture": [("mapping table", ["Product component", "component|Pattern", "Role"])],
    "Non-functional requirements": [("NFR table", ["Area", "Requirement"])],
    "Metrics and success criteria": [("metrics table", ["Metric", "Definition", "Target"])],
    "Scope, phases, and release plan": [("phase table", ["Phase", "Ships", "Gate"])],
    "Risks and open questions": [("risk table", ["Risk", "Mitigation"])],
}

FORBIDDEN = [r"\bTBD\b", r"\bTODO\b", r"\bTBC\b", r"to be defined", r"to be decided", r"\bFIXME\b"]
VAGUE = [r"\bfast\b(?!-moving)", r"\brobust\b", r"\bscalable\b", r"user-friendly", r"\bappropriate\b",
         r"\breasonable\b", r"\bseamless\b", r"\bintuitive\b", r"\bhighly\b"]
JUDGMENT = r"\b(grade[sd]?|grading|adjudicat\w*|approv\w*|score[sd]?|scoring|rank\w*|accept\w* or declin\w*)\b"


def split_h2(lines):
    secs, cur, buf = [], None, []
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            if cur is not None:
                secs.append((cur, buf))
            cur, buf = m.group(1).strip(), []
        elif cur is not None:
            buf.append(ln)
    if cur is not None:
        secs.append((cur, buf))
    return secs


def tables(lines):
    for i in range(len(lines) - 1):
        if lines[i].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[i + 1]):
            hdr = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            yield hdr, rows


def has_col(col, hdr):
    return any(any(alt.lower() in h.lower() for h in hdr) for alt in col.split("|"))


def find_table(body, cols):
    for hdr, rows in tables(body):
        if all(has_col(c, hdr) for c in cols):
            return hdr, rows
    return None, None


def has_number(s):
    return bool(re.search(r"\d", s)) or bool(re.search(r"WCAG|LGPD|GDPR|ISO|SOC|IEC|NIST|HIPAA", s))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    text = open(sys.argv[1], encoding="utf-8").read()
    lines = text.splitlines()
    fails, warns = [], []

    # Header
    if not lines or not re.match(r"^#\s+PRD\s+[—-]\s+\S", lines[0]):
        fails.append("H1 must be '# PRD — <Product name>' on line 1")
    head = "\n".join(lines[:5])
    if not re.search(r"\b(19|20)\d{2}\b", head):
        fails.append("byline must carry a date")
    if not re.search(r"\bv\d+\.\d+", head):
        warns.append("byline has no version (v1.0); the TRD traces to it")

    secs = split_h2(lines)
    titles = [t for t, _ in secs]
    by_title = {t: b for t, b in secs}

    # Fixed headings present and ordered
    idx = []
    for t in FIXED_ORDER:
        if t not in titles:
            fails.append(f"missing section heading '## {t}' (exact text; it is a TRD anchor)")
        else:
            idx.append(titles.index(t))
    if idx != sorted(idx):
        fails.append(f"fixed sections out of order; expected {FIXED_ORDER}")

    # Capabilities
    caps = [(t, b) for t, b in secs if re.match(r"^Capability\s+\d+\s+[—-]\s+\S", t)]
    if not caps:
        fails.append("no '## Capability N — Name' sections")
    nums = [int(re.match(r"^Capability\s+(\d+)", t).group(1)) for t, _ in caps]
    if nums and nums != list(range(1, len(nums) + 1)):
        fails.append(f"capabilities must be numbered 1..N in order, got {nums}")
    if caps and "Users and personas" in titles and "Architecture" in titles:
        first_cap = titles.index(caps[0][0])
        if not (titles.index("Users and personas") < first_cap < titles.index("Architecture")):
            fails.append("capability sections must sit between 'Users and personas' and 'Architecture'")
    for t, b in caps:
        body = "\n".join(b)
        if not re.search(r"^Requirements:\s*$", body, re.M):
            fails.append(f"'{t}': missing a 'Requirements:' list")
        bullets = [l for l in b if re.match(r"^\s*[-*]\s+\S", l)]
        if len(bullets) < 5:
            fails.append(f"'{t}': {len(bullets)} requirement bullets; need ≥ 5 testable ones")
        if not any(re.search(r"\d", l) for l in bullets):
            warns.append(f"'{t}': no requirement carries a number")
        if not re.search(r"\b(refus\w*|reject\w*|replaced|declin\w*|kill\w*|not accepted|never|Limits?:)", body, re.I):
            warns.append(f"'{t}': no refusal, failure or limit behaviour stated")
        if "Screens:" not in body:
            warns.append(f"'{t}': no 'Screens:' line (optional; the TRD maps IDs to routes)")

    # Summary capability table vs capability count
    if "Summary" in by_title:
        hdr, rows = find_table(by_title["Summary"], TABLES["Summary"][0][1])
        if rows is not None and caps and len(rows) != len(caps):
            warns.append(f"Summary table has {len(rows)} rows but there are {len(caps)} capability sections")

    # Tables and their numeric cells
    for sec, reqs in TABLES.items():
        if sec not in by_title:
            continue
        for label, cols in reqs:
            hdr, rows = find_table(by_title[sec], cols)
            if hdr is None:
                fails.append(f"'{sec}': {label} missing or missing columns {cols}")
                continue
            if sec == "Problem and goals":
                for r in rows:
                    if len(r) >= 2 and not has_number(r[1]):
                        fails.append(f"goal '{r[0][:40]}': target has no number")
            if sec == "Metrics and success criteria":
                for r in rows:
                    if len(r) >= 3 and not has_number(r[2]):
                        fails.append(f"metric '{r[0][:40]}': target has no number")
            if sec == "Scope, phases, and release plan":
                for r in rows:
                    if len(r) >= 3 and not has_number(r[2]):
                        fails.append(f"phase '{r[0][:40]}': gate has no number")
            if sec == "Non-functional requirements":
                areas = [r[0] for r in rows if r]
                for a in NFR_AREAS:
                    if not any(a.lower() == x.lower() for x in areas):
                        (fails if a in NFR_REQUIRED else warns).append(
                            f"NFR table missing row '{a}' (TRD anchor §Non-functional · {a})")
                for r in rows:
                    if len(r) >= 2 and not has_number(r[1]):
                        warns.append(f"NFR '{r[0]}': no number or named standard")
            if sec == "Risks and open questions":
                for r in rows:
                    if len(r) >= 2 and len(r[1]) < 40:
                        warns.append(f"risk '{r[0][:40]}': mitigation is thin; name control, detection, consequence")

    # Boundaries
    if "Problem and goals" in by_title and "Non-goals:" not in "\n".join(by_title["Problem and goals"]):
        fails.append("'Problem and goals' must contain 'Non-goals:'")
    if "Metrics and success criteria" in by_title and "not measured" not in "\n".join(by_title["Metrics and success criteria"]).lower():
        fails.append("'Metrics and success criteria' must contain 'What is not measured:'")
    if "Scope, phases, and release plan" in by_title:
        body = "\n".join(by_title["Scope, phases, and release plan"])
        if "Out of scope" not in body:
            fails.append("'Scope, phases, and release plan' must contain 'Out of scope …'")
        if "Dependencies:" not in body:
            warns.append("'Scope, phases, and release plan': no 'Dependencies:' sentence")
    if "Risks and open questions" in by_title:
        body = by_title["Risks and open questions"]
        txt = "\n".join(body)
        if "Open questions:" not in txt:
            fails.append("'Risks and open questions' must contain 'Open questions:'")
        else:
            after = txt.split("Open questions:", 1)[1]
            qs = [l for l in after.splitlines() if re.match(r"^\s*[-*]\s+\S", l)]
            if len(qs) < 3:
                fails.append(f"only {len(qs)} open questions; need ≥ 3, each a choice with options")
            for q in qs:
                if "?" not in q and " or " not in q:
                    warns.append(f"open question not phrased as a choice: {q.strip()[:60]}")

    # Instrument sections where judgments are made
    cap_text = "\n".join("\n".join(b) for _, b in caps)
    judges = bool(re.search(JUDGMENT, cap_text, re.I))
    instrument = any(
        find_table(b, ["Tier", "Examples", "Base score"])[0] is not None
        or find_table(b, ["Accept", "Floor"])[0] is not None
        for t, b in secs if t not in FIXED_ORDER and not t.startswith("Capability"))
    if judges and not instrument:
        fails.append("a capability grades/approves/adjudicates but no instrument section "
                     "(tiers, thresholds, worked examples) exists")
    if instrument:
        for t, b in secs:
            if t in FIXED_ORDER or t.startswith("Capability"):
                continue
            body = "\n".join(b)
            if find_table(b, ["Accept", "Floor"])[0] is not None:
                if "Worked examples:" not in body:
                    fails.append(f"'{t}': instrument has no 'Worked examples:'")
                if not re.search(r"always", body, re.I):
                    warns.append(f"'{t}': no 'human always' class for what the instrument must not decide")
                if not re.search(r"version", body, re.I):
                    warns.append(f"'{t}': instrument not stated as versioned and published")
                # arithmetic check on worked examples: a × b × c = d
                for m in re.finditer(r"(\d+(?:\.\d+)?)((?:\s*[×x\*]\s*\d+(?:\.\d+)?)+)\s*=\s*(\d+(?:\.\d+)?)", body):
                    val = float(m.group(1))
                    for f in re.findall(r"\d+(?:\.\d+)?", m.group(2)):
                        val *= float(f)
                    if abs(val - float(m.group(3))) > 0.51:
                        fails.append(f"'{t}': worked example arithmetic wrong: {m.group(0)}")

    # Closure and vagueness
    for pat in FORBIDDEN:
        for m in re.finditer(pat, text, re.I):
            fails.append(f"line {text[:m.start()].count(chr(10)) + 1}: unresolved placeholder '{m.group(0)}' — make it an open question")
    for pat in VAGUE:
        for m in re.finditer(pat, text, re.I):
            ln = text[:m.start()].count("\n") + 1
            warns.append(f"line {ln}: '{m.group(0)}' hides a number; state the value")
    for m in re.finditer(r"<[A-Z][^<>\n]{3,80}>", text):
        if m.group(0).startswith(("<br", "<!--")):
            continue
        fails.append(f"line {text[:m.start()].count(chr(10)) + 1}: template placeholder left in: {m.group(0)[:50]}")

    for w in warns:
        print(f"WARN  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    print(f"\n{len(fails)} fail, {len(warns)} warn")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
