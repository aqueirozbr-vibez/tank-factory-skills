#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""PRD lint for docs/prd/<product>.md (Tank Factory v3 fixed shape).

Usage: python3 lint_prd.py docs/prd/<product>.md [--mode new|amendment|as-built]
                           [--impact docs/initiatives/<id>/impact.md]

Checks the fixed headings (the anchors every other artifact cites), the seven
PRD building blocks (user roles, jobs to be done, journey flowchart, screens
map, objects, functional and non-functional requirements), the Principles
section (≤ 10 articles, each with its compliance check), stable ids and
closure. Exit 1 on any FAIL; WARN lines never fail the run.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

FIXED = ["Summary", "Problem and goals", "Principles", "Users and personas", "Journeys and screens",
         "Objects", "Architecture", "Non-functional requirements", "Metrics and success criteria",
         "Scope, phases, and release plan", "Risks and open questions"]
NFR_REQUIRED = ["Security", "Privacy", "Performance", "Availability", "Accessibility", "Auditability"]
SCREEN = r"\b[A-Z]{1,3}-\d{2,3}\b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--mode", default=None, choices=["new", "amendment", "as-built"])
    ap.add_argument("--impact")
    ap.add_argument("--research", help="research report; every support system in its Customer blueprint must reach the Service blueprint")
    a = ap.parse_args()
    text = md.read(a.path)
    rep = md.Report("PRD lint")
    lines = text.splitlines()
    head = "\n".join(lines[:5])
    mode = a.mode or (re.search(r"mode\s+(new|amendment|as-built)", head) or [None, "new"])[1]

    if not lines or not re.match(r"^#\s+PRD\s+[—-]\s+\S", lines[0]):
        rep.fail("H1 must be '# PRD — <Product name>' on line 1")
    if not re.search(r"\b(19|20)\d{2}\b", head):
        rep.fail("byline must carry a date")
    if not re.search(r"\bv\d+\.\d+", head):
        rep.fail("byline must carry a version (v1.0); the TRD traces to it")
    if "traces to" not in head:
        rep.fail("byline must say what the PRD traces to (the research report, or the brief id when there is none)")

    secs = md.sections(text)
    titles = [t for t, _ in secs]
    by = dict(secs)

    idx = []
    for t in FIXED:
        if t not in by:
            rep.fail(f"missing section '## {t}' (exact text; it is an anchor)")
        else:
            idx.append(titles.index(t))
    if idx != sorted(idx):
        rep.fail(f"fixed sections out of order; expected {FIXED}")

    caps = [(t, b) for t, b in secs if re.match(r"^Capability\s+\d+\s+[—-]\s+\S", t)]
    nums = [int(re.match(r"^Capability\s+(\d+)", t).group(1)) for t, _ in caps]
    if not caps:
        rep.fail("no '## Capability N — Name' sections")
    elif nums != list(range(1, len(nums) + 1)):
        rep.fail(f"capabilities must be numbered 1..N in order, got {nums}")
    if caps and "Objects" in by and "Architecture" in by:
        first = titles.index(caps[0][0])
        if not titles.index("Objects") < first < titles.index("Architecture"):
            rep.fail("capability sections sit between 'Objects' and 'Architecture'")

    # Summary
    kind = None
    if "Summary" in by:
        kind = (md.labelled(by["Summary"], "Product kind") or "").strip("`* ").lower()
        if kind not in {"ui", "service", "ui_and_service"}:
            rep.fail("Summary: 'Product kind:' must be ui, service or ui_and_service")
        hdr, rows = md.table(by["Summary"], ["Capability", "What the user does", "guarantees"])
        if hdr is None:
            rep.fail("Summary: capability table missing (Capability | What the user does | What the system guarantees)")
        elif caps and len(rows) != len(caps):
            rep.fail(f"Summary table has {len(rows)} rows but there are {len(caps)} capability sections")

    # Goals
    if "Problem and goals" in by:
        b = by["Problem and goals"]
        hdr, rows = md.table(b, ["Goal", "Target", "Measure"])
        if hdr is None:
            rep.fail("Problem and goals: goals table missing (Goal | Target | Measure)")
        for r in rows:
            if not md.has_number(md.cell(r, hdr, "Target")):
                rep.fail(f"goal '{r[0][:40]}': target has no number")
        if "Non-goals:" not in b:
            rep.fail("Problem and goals: 'Non-goals:' missing")

    # Principles
    if "Principles" in by:
        hdr, rows = md.table(by["Principles"], ["Article", "Principle", "Compliance check"])
        if hdr is None:
            rep.fail("Principles: table missing (Article | Principle | Compliance check)")
        else:
            if not rows:
                rep.fail("Principles: no articles")
            if len(rows) > 10:
                rep.fail(f"Principles: {len(rows)} articles; the limit is 10")
            for r in rows:
                art = md.cell(r, hdr, "Article").strip("` ")
                if not re.match(r"^P-\d+$", art):
                    rep.fail(f"Principles: article id '{art}' must be P-<n>")
                if md.is_empty(md.cell(r, hdr, "Compliance check")):
                    rep.fail(f"Principles {art}: no compliance check")
                if mode == "as-built" and "inferred" not in " ".join(r).lower():
                    rep.fail(f"Principles {art}: as-built principles are marked 'inferred'")

    all_fr = set(md.ids(text, r"\bFR-\d+\.\d+\b"))
    defined_fr, defined_sc, features = set(), [], []
    role_ids = set()

    # Capabilities
    screens_on_lines = set()
    for t, b in caps:
        n = re.match(r"^Capability\s+(\d+)", t).group(1)
        reqs = [x for x in md.bullets(b) if re.match(r"^FR-" + n + r"\.\d+\s*:", x)]
        scs = [x for x in md.bullets(b) if re.match(r"^SC-\d+\b[^:]*:", x)]
        feats = re.findall(r"^\s*[-*]\s+`([a-z0-9][a-z0-9-]*)`\s+[—-]", b, re.M)
        for x in reqs:
            defined_fr.add(x.split(":")[0].strip())
        defined_sc += [re.match(r"^SC-\d+", x).group(0) for x in scs]
        features += feats
        owners = [m.group(1) for x in scs for m in [re.match(r"^SC-\d+\s*\(`([a-z0-9-]+)`\)\s*:", x)] if m]
        if len(owners) != len(scs):
            rep.fail(f"'{t}': each success criterion names its feature: SC-n (`feature-slug`): text")
        for o in owners:
            if o not in feats:
                rep.fail(f"'{t}': a success criterion names feature `{o}`, which is not under Features:")
        for f in feats:
            if f not in owners:
                rep.fail(f"'{t}': feature `{f}` has no success criterion, so nothing will test it")
        if "Requirements:" not in b or len(reqs) < 3:
            rep.fail(f"'{t}': {len(reqs)} requirements with ids FR-{n}.m; need ≥ 3")
        if "Success criteria:" not in b or not scs:
            rep.fail(f"'{t}': no success criteria with ids SC-n")
        if "Features:" not in b or not feats:
            rep.fail(f"'{t}': no features (`slug` — text); each becomes a feature file")
        if not any(re.search(r"\d", x) for x in reqs):
            rep.warn(f"'{t}': no requirement carries a number")
        if not re.search(r"\b(refus\w*|reject\w*|declin\w*|never|not accepted)\b", b, re.I):
            rep.warn(f"'{t}': no refusal or failure behaviour stated")
        if md.labelled(b, "Limits") is None:
            rep.warn(f"'{t}': no 'Limits:' line")
        sline = md.labelled(b, "Screens")
        if sline is None:
            if kind in {"ui", "ui_and_service"}:
                rep.warn(f"'{t}': no 'Screens:' line; a screen missing from these lines is never drawn")
        else:
            screens_on_lines |= set(re.findall(SCREEN, sline))
        if mode == "as-built" and not re.search(r"`[^`]*(/|\.)[^`]*`", b):
            rep.fail(f"'{t}': as-built capability must cite ≥ 1 code path or route in backticks")
    dup = sorted({s for s in defined_sc if defined_sc.count(s) > 1})
    if dup:
        rep.fail(f"success criteria ids used twice: {dup}")
    if len(set(features)) != len(features):
        rep.fail("feature slugs must be unique across capabilities")

    # Users, roles, jobs
    if "Users and personas" in by:
        b = by["Users and personas"]
        hdr, rows = md.table(b, ["Persona", "Who", "Primary use", "Must have"])
        personas = [r[0].strip("*` ") for r in rows]
        if hdr is None or not rows:
            rep.fail("Users and personas: persona table missing (Persona | Who | Primary use | Must have)")
        rh, rrows = md.table(md.section(b, "User roles", 3) or "", ["Role", "Personas", "Permissions", "Never"])
        role_ids = {r[0].strip("*` ") for r in rrows}
        if rh is None or not rrows:
            rep.fail("Users and personas: '### User roles' table missing (Role | Personas | Permissions | Never)")
        else:
            served = " ".join(md.cell(r, rh, "Personas") for r in rrows)
            for p in personas:
                if p not in served:
                    rep.fail(f"persona '{p}' maps to no user role")
            for r in rrows:
                if md.is_empty(md.cell(r, rh, "Permissions")):
                    rep.fail(f"role '{r[0]}': no permissions")
        jh, jrows = md.table(md.section(b, "Jobs to be done", 3) or "",
                             ["Job", "Role", "When", "I want", "So I can", "Success number", "Requirements"])
        if jh is None or not jrows:
            rep.fail("Users and personas: '### Jobs to be done' table missing "
                     "(Job | Role | When | I want to | So I can | Success number | Requirements)")
        else:
            roles = {r[0].strip("*` ") for r in rrows}
            for r in jrows:
                job = r[0].strip("` ")
                if not re.match(r"^JTBD-\d+$", job):
                    rep.fail(f"job id '{job}' must be JTBD-<n>")
                if roles and md.cell(r, jh, "Role").strip("*` ") not in roles:
                    rep.fail(f"{job}: role '{md.cell(r, jh, 'Role')}' is not in User roles")
                if not md.has_number(md.cell(r, jh, "Success number")):
                    rep.fail(f"{job}: success has no number")
                cited = re.findall(r"FR-\d+\.\d+", md.cell(r, jh, "Requirements"))
                if not cited:
                    rep.fail(f"{job}: cites no functional requirement")
                for c in cited:
                    if c not in defined_fr:
                        rep.fail(f"{job}: cites {c}, which no capability defines")

    # Objects
    objects = []
    if "Objects" in by:
        b = by["Objects"]
        oh, orows = md.table(b, ["Object", "Definition", "Owner", "States", "Retention", "Personal data"])
        if oh is None or not orows:
            rep.fail("Objects: index table missing (Object | Definition | Owner role | States | Retention | Personal data)")
        objects = [r[0].strip("*` ") for r in orows]
        subs = dict(md.sections(b, 3))
        for r in orows:
            name = r[0].strip("*` ")
            for c in ("Definition", "Owner", "States", "Retention", "Personal data"):
                if md.is_empty(md.cell(r, oh, c)):
                    rep.fail(f"object '{name}': empty '{c}'")
            if name not in subs:
                rep.fail(f"object '{name}': no '### {name}' section with its fields")
                continue
            fh, frows = md.table(subs[name], ["Field", "Type", "Required", "Format", "Example"])
            if fh is None or not frows:
                rep.fail(f"object '{name}': fields table missing (Field | Type | Required | Format | Example)")
            for fr in frows:
                for c in ("Type", "Example"):
                    if md.is_empty(md.cell(fr, fh, c)):
                        rep.fail(f"object '{name}' field '{fr[0]}': no {c.lower()}")

    # Journeys and screens
    if "Journeys and screens" in by:
        b = by["Journeys and screens"]
        if kind == "service":
            if screens_on_lines:
                rep.fail("product kind is service but capabilities name screens")
            if "no screens" not in b.lower():
                rep.fail("Journeys and screens: a service product writes 'No screens: service product.'")
        else:
            flow = md.mermaid(b, "flowchart") + md.mermaid(b, "graph")
            if not flow:
                rep.fail("Journeys and screens: Mermaid flowchart missing under '### User journey flowchart'")
            sh, srows = md.table(b, ["Screen", "Name", "Purpose", "Roles", "Objects", "Leads to"])
            if sh is None or not srows:
                rep.fail("Journeys and screens: screens map missing (Screen | Name | Purpose | Roles | Objects | Leads to)")
            mapped = set()
            for r in srows:
                sid = r[0].strip("*` ")
                mapped.add(sid)
                if not re.match("^" + SCREEN[2:-2] + "$", sid):
                    rep.fail(f"screen id '{sid}' must look like S-01")
                if flow and not any(sid in f for f in flow):
                    rep.fail(f"screen {sid} does not appear in the journey flowchart")
                for role in [x.strip("*` ") for x in re.split(r"[,;]", md.cell(r, sh, "Roles")) if x.strip()]:
                    if role_ids and role not in role_ids:
                        rep.fail(f"screen {sid}: role '{role}' is not in User roles")
                for o in [x.strip("*` ") for x in re.split(r"[,;]", md.cell(r, sh, "Objects")) if x.strip()]:
                    if objects and o not in objects and not md.is_empty(o):
                        rep.fail(f"screen {sid}: object '{o}' is not defined in Objects")
            for r in srows:
                for sid in set(re.findall(SCREEN, md.cell(r, sh, "Leads to"))) - mapped:
                    rep.fail(f"screen {r[0]}: leads to {sid}, which is not in the screens map")
            for f in flow:
                for sid in set(re.findall(SCREEN, f)) - mapped:
                    rep.fail(f"flowchart names {sid}, which is not in the screens map")
                if "{" in f and f.count("-->|") + f.count("-- ") < 2:
                    rep.warn("flowchart has a decision without two labelled branches")
            for sid in sorted(mapped - screens_on_lines):
                rep.fail(f"screen {sid} is on no capability's 'Screens:' line, so no one will draw it")
            for sid in sorted(screens_on_lines - mapped):
                rep.fail(f"'Screens:' line names {sid}, which is not in the screens map")
            if kind in {"ui", "ui_and_service"} and not screens_on_lines:
                rep.fail(f"product kind is {kind} but no capability has a 'Screens:' line")

    # Service blueprint: the future service, with the product in it
    if "Journeys and screens" in by:
        b = by["Journeys and screens"]
        _, maprows = md.table(b, ["Screen", "Name", "Purpose", "Roles", "Objects", "Leads to"])
        map_ids = {r[0].strip("*` ") for r in maprows}
        bh, brows = md.table(b, ["Step", "Screen", "Frontstage", "Backstage", "Support system",
                                 "Failure point", "Recovery", "Requirements"])
        if bh is None or not brows:
            rep.fail("Journeys and screens: service blueprint missing under '### Service blueprint' "
                     "(Step | Screen | Frontstage | Backstage | Support system | Failure point | Recovery | Requirements)")
        else:
            steps, on_blueprint, systems = set(), set(), set()
            for r in brows:
                step = r[0].strip("*` ")
                if not re.match(r"^B-\d+$", step):
                    rep.fail(f"Service blueprint: step id '{step}' must be B-<n>")
                if step in steps:
                    rep.fail(f"Service blueprint: step {step} appears twice")
                steps.add(step)
                for sid in re.findall(SCREEN, md.cell(r, bh, "Screen")):
                    on_blueprint.add(sid)
                    if map_ids and sid not in map_ids:
                        rep.fail(f"Service blueprint {step}: screen {sid} is not in the screens map")
                if md.is_empty(md.cell(r, bh, "Backstage")):
                    rep.fail(f"Service blueprint {step}: say what the product does backstage")
                cited = re.findall(r"FR-\d+\.\d+", md.cell(r, bh, "Requirements"))
                if not cited:
                    rep.fail(f"Service blueprint {step}: cite the FR- requirements that make the step happen")
                for c in cited:
                    if defined_fr and c not in defined_fr:
                        rep.fail(f"Service blueprint {step}: {c} is not a requirement in this PRD")
                failure = md.cell(r, bh, "Failure point")
                if not md.is_empty(failure, allow=("none",)) and failure.strip("*` ").lower() != "none" \
                        and md.is_empty(md.cell(r, bh, "Recovery")):
                    rep.fail(f"Service blueprint {step}: failure point '{failure}' has no recovery")
                for s in re.split(r"[,;]", md.cell(r, bh, "Support system")):
                    s = s.strip("*` ").lower()
                    if s and not md.is_empty(s, allow=()) and s != "none":
                        systems.add(s)
            for sid in sorted(map_ids - on_blueprint):
                rep.fail(f"Service blueprint: screen {sid} is on no step")
            if a.research:
                rh, rrows = md.table(md.read(a.research), ["Step", "Frontstage", "Backstage", "Support system"])
                for s in sorted({md.cell(r, rh, "Support system").strip("*` ") for r in rrows} - {""}):
                    if s.lower() not in systems:
                        rep.fail(f"Service blueprint: support system '{s}' from the research blueprint is on no step")

    # Fixed tables with numbers
    if "Architecture" in by and md.table(by["Architecture"], ["Product component", "Pattern", "Role"])[0] is None:
        rep.fail("Architecture: mapping table missing (Product component | Pattern | Role)")
    if "Non-functional requirements" in by:
        hdr, rows = md.table(by["Non-functional requirements"], ["Area", "Requirement"])
        if hdr is None:
            rep.fail("Non-functional requirements: table missing (Area | Requirement)")
        areas = [r[0].strip("*` ").lower() for r in rows]
        for need in NFR_REQUIRED:
            if need.lower() not in areas:
                rep.fail(f"NFR table missing row '{need}'")
        for r in rows:
            if not md.has_number(md.cell(r, hdr, "Requirement")):
                rep.fail(f"NFR '{r[0]}': no number or named standard")
    if "Metrics and success criteria" in by:
        b = by["Metrics and success criteria"]
        hdr, rows = md.table(b, ["Metric", "Definition", "Target"])
        if hdr is None:
            rep.fail("Metrics and success criteria: table missing (Metric | Definition | Target)")
        for r in rows:
            if not md.has_number(md.cell(r, hdr, "Target")):
                rep.fail(f"metric '{r[0][:40]}': target has no number")
        if "not measured" not in b.lower():
            rep.fail("Metrics and success criteria: 'What is not measured:' missing")
    if "Scope, phases, and release plan" in by:
        b = by["Scope, phases, and release plan"]
        hdr, rows = md.table(b, ["Phase", "Ships", "Gate"])
        if hdr is None:
            rep.fail("Scope, phases, and release plan: table missing (Phase | Ships | Gate)")
        for r in rows:
            if not md.has_number(md.cell(r, hdr, "Gate")):
                rep.fail(f"phase '{r[0][:40]}': gate has no number")
        if "Out of scope" not in b:
            rep.fail("Scope, phases, and release plan: 'Out of scope' paragraph missing")
    if "Risks and open questions" in by:
        b = by["Risks and open questions"]
        hdr, rows = md.table(b, ["Risk", "Mitigation"])
        if hdr is None:
            rep.fail("Risks and open questions: table missing (Risk | Mitigation)")
        for r in rows:
            if len(md.cell(r, hdr, "Mitigation")) < 40:
                rep.warn(f"risk '{r[0][:40]}': mitigation is thin; name control, detection and consequence")
        if "Open questions:" not in b:
            rep.fail("Risks and open questions: 'Open questions:' missing (write 'None.' when there are none)")
        else:
            qs = md.bullets(b.split("Open questions:", 1)[1])
            for q in qs:
                if "?" not in q or not re.search(r"\bor\b|,|/", q):
                    rep.warn(f"open question not phrased as a choice with its options: {q[:60]}")
            if "(assumed)" in text and not qs:
                rep.fail("values are marked (assumed) but Open questions lists none; each assumed value is a question for the product owner")

    for fr in sorted(all_fr - defined_fr):
        rep.fail(f"{fr} is cited but no capability defines it")

    if mode == "as-built":
        for i, ln in enumerate(lines, 1):
            if re.search(r"\binferred\b", ln) and "`" not in ln and not ln.startswith("#") and "Principles" not in ln:
                rep.warn(f"line {i}: 'inferred' without evidence in backticks")
    if mode == "amendment" or a.impact:
        if not a.impact or not os.path.exists(a.impact):
            rep.fail("amendment mode needs --impact docs/initiatives/<id>/impact.md")
        else:
            it = md.read(a.impact)
            for s in ("Sections changed", "Units affected", "ADRs touched"):
                if md.section(it, s) is None:
                    rep.fail(f"impact report: missing '## {s}'")

    md.check_placeholders(text, rep, "PRD")
    md.check_vague(text, rep, "PRD")
    rep.finish()


if __name__ == "__main__":
    main()
