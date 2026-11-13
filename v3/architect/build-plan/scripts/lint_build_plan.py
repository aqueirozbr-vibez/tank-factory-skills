#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Build-plan gate for specs/00-build-plan.md.

Usage: python3 lint_build_plan.py specs/00-build-plan.md [--prd docs/prd/<product>.md]
           [--trd docs/trd/<product>.md] [--max-units 60] [--emit-units]

Checks the gate — acyclic dependencies that all point to earlier units, one
boundary per unit, a build phase per unit, the unit limit — and that every
unit has a verifiable result and a verify list, every functional requirement
and success criterion is carried by a unit, cited TRD sections exist and
boundaries are folders from the TRD's component map.
--emit-units prints the envelope's units[] as JSON instead of the report.
Exit 1 on any FAIL.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

LINES = ["Goal", "Repository", "Boundary", "Build phase", "Depends on", "Dependencies",
         "Cites", "Scenarios", "Verifiable result"]


def parse_units(text, rep):
    units = []
    body = md.section(text, "Units")
    if body is None:
        rep.fail("missing '## Units'")
        return units
    for title, b in md.sections(body, 3):
        m = re.match(r"^Unit\s+(\d+)\s+[—-]\s+(\S.*)$", title)
        if not m:
            rep.fail(f"unit heading '### {title}' must be '### Unit <n> — <Name>'")
            continue
        n, u = int(m.group(1)), {"n": int(m.group(1)), "name": m.group(2).strip()}
        for lab in LINES:
            v = md.labelled(b, lab)
            if v is None or (md.is_empty(v, allow=("none",)) and lab not in ("Depends on",)):
                rep.fail(f"unit {n}: '{lab}:' line missing or empty")
            u[lab] = v or ""
        u["cancelled"] = u["Goal"].lower().startswith("cancelled")
        bnds = re.findall(r"`([^`]+)`", u["Boundary"])
        if len(bnds) != 1:
            rep.fail(f"unit {n}: {len(bnds)} boundaries; a unit has exactly one folder in backticks")
        u["boundary"] = bnds[0] if bnds else ""
        ph = re.search(r"\d+", u["Build phase"])
        if not ph:
            rep.fail(f"unit {n}: build phase is not a number")
        u["build_phase"] = int(ph.group(0)) if ph else 0
        dep = u["Depends on"].strip().lower()
        u["depends_on"] = [] if dep in ("", "none", "—", "-") else [int(x) for x in re.findall(r"\d+", dep)]
        d = u["Dependencies"].strip()
        u["dependencies"] = [] if d.lower().startswith("none") else re.findall(r"`([^`]+)`", d)
        for p in u["dependencies"]:
            if not re.match(r"^@?[\w./-]+@\d[\w.\-+]*$", p):
                rep.fail(f"unit {n}: dependency '{p}' must be name@version")
        if d and not d.lower().startswith("none") and not u["dependencies"]:
            rep.fail(f"unit {n}: dependencies must be in backticks as name@version, or 'none'")
        vb = b.split("Verify:", 1)[1] if "Verify:" in b else ""
        u["verify"] = md.bullets(vb)
        if not u["verify"] and not u["cancelled"]:
            rep.fail(f"unit {n}: empty verify list")
        if not re.match(r"^[\w.-]+/[\w.-]+$", u["Repository"].strip("` ")):
            rep.fail(f"unit {n}: repository must be owner/name")
        sc = u["Scenarios"]
        if not sc.lower().startswith("none") and not re.search(r"\.feature", sc):
            rep.fail(f"unit {n}: scenarios must name a feature file and tags, or 'none: <why>'")
        if sc.lower().startswith("none") and len(sc) < 12:
            rep.fail(f"unit {n}: 'Scenarios: none' needs its reason")
        units.append(u)
    return units


def cited_headings(cites, doc):
    """Headings cited as '<doc> §<heading> (ids)'; a trailing parenthesis of ids is not part of the heading."""
    out = []
    for part in cites.split(";"):
        m = re.search(doc + r"\s+§\s*(.+)$", part.strip())
        if m:
            out.append(re.sub(r"\s*\([^()]*\b(?:FR|SC|P|INV)-\d[^()]*\)\s*$", "", m.group(1)).strip())
    return out


def find_cycle(units):
    graph = {u["n"]: u["depends_on"] for u in units}
    state = {}

    def visit(n, path):
        if state.get(n) == 2:
            return None
        if state.get(n) == 1:
            return path[path.index(n):] + [n]
        state[n] = 1
        for d in graph.get(n, []):
            c = visit(d, path + [n])
            if c:
                return c
        state[n] = 2
        return None

    for n in graph:
        c = visit(n, [])
        if c:
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--prd")
    ap.add_argument("--trd")
    ap.add_argument("--max-units", type=int, default=60)
    ap.add_argument("--emit-units", action="store_true")
    a = ap.parse_args()
    text = md.read(a.path)
    rep = md.Report("build-plan gate")
    lines = text.splitlines()
    if not lines or not re.match(r"^#\s+Build plan\s+[—-]\s+\S", lines[0]):
        rep.fail("H1 must be '# Build plan — <Product name>' on line 1")
    if not re.search(r"mode\s+(new|delta)", "\n".join(lines[:5])):
        rep.fail("byline must say 'mode new' or 'mode delta'")

    units = parse_units(text, rep)
    live = [u for u in units if not u["cancelled"]]
    if a.emit_units:
        print(json.dumps([{"n": u["n"], "name": u["name"], "boundary": u["boundary"], "depends_on": u["depends_on"],
                           "dependencies": u["dependencies"], "build_phase": u["build_phase"]} for u in live], indent=2))
        sys.exit(1 if rep.fails else 0)

    nums = [u["n"] for u in units]
    if nums != list(range(1, len(nums) + 1)):
        rep.fail(f"units must be numbered 1..N with no gaps, in order; got {nums[:12]}")
    if len(live) > a.max_units:
        rep.fail(f"{len(live)} units; the limit is {a.max_units} — the brief returns for splitting")
    if not units:
        rep.fail("no units")

    by_n = {u["n"]: u for u in units}
    for u in live:
        for d in u["depends_on"]:
            if d not in by_n:
                rep.fail(f"unit {u['n']}: depends on unit {d}, which does not exist")
            elif d >= u["n"]:
                rep.fail(f"unit {u['n']}: depends on unit {d}, which is not earlier")
            elif by_n[d]["build_phase"] > u["build_phase"]:
                rep.fail(f"unit {u['n']} (phase {u['build_phase']}) depends on unit {d} in a later phase ({by_n[d]['build_phase']})")
            elif by_n[d]["cancelled"]:
                rep.fail(f"unit {u['n']}: depends on cancelled unit {d}")
    cyc = find_cycle(live)
    if cyc:
        rep.fail("dependency cycle: " + " → ".join(str(x) for x in cyc))

    # Phases table
    ph, prows = md.table(md.section(text, "Build phases") or "", ["Phase", "Goal", "Units", "Exit check"])
    if ph is None or not prows:
        rep.fail("'## Build phases' table missing (Phase | Goal | Units | Exit check)")
    else:
        listed = {int(m.group(0)) for r in prows for m in [re.search(r"\d+", r[0])] if m}
        for u in live:
            if u["build_phase"] not in listed:
                rep.fail(f"unit {u['n']}: build phase {u['build_phase']} is not in the Build phases table")
        for r in prows:
            if not md.has_number(md.cell(r, ph, "Exit check")) and "@SC-" not in md.cell(r, ph, "Exit check"):
                rep.fail(f"phase {r[0]}: exit check has no number or named scenario")

    # Dependencies per phase
    dh, drows = md.table(md.section(text, "Dependencies per build phase") or "", ["Phase", "Repository", "Package", "Needed by"])
    if dh is None:
        rep.fail("'## Dependencies per build phase' table missing (Phase | Repository | Package | Needed by)")
    else:
        listed = {(int(m.group(0)), p) for r in drows for m in [re.search(r"\d+", r[0])] if m
                  for p in re.findall(r"`([^`]+)`", md.cell(r, dh, "Package"))}
        for u in live:
            for p in u["dependencies"]:
                if not any(pk == p and phn <= u["build_phase"] for phn, pk in listed):
                    rep.fail(f"unit {u['n']}: package {p} is not listed for build phase {u['build_phase']} or earlier")

    # Coverage against the PRD
    cited = " ".join(u["Cites"] for u in live)
    scen = " ".join(u["Scenarios"] for u in live)
    if a.prd:
        prd = md.read(a.prd)
        for fr in md.ids(prd, r"(?m)^\s*[-*]\s+(FR-\d+\.\d+)\s*:") or []:
            if not re.search(re.escape(fr) + r"(?!\d)", cited):
                rep.fail(f"{fr} is carried by no unit")
        for sc in md.ids(prd, r"(?m)^\s*[-*]\s+(SC-\d+)\b[^:\n]*:") or []:
            if not re.search(r"@" + re.escape(sc) + r"(?!\d)", scen):
                rep.fail(f"{sc} is attached to no unit's scenarios")
        heads = {t for t, _ in md.sections(prd)}
        for u in live:
            for h in cited_headings(u["Cites"], "PRD"):
                if h.strip() and h.strip() not in heads:
                    rep.fail(f"unit {u['n']}: cites PRD §{h.strip()}, which is not a PRD heading")
    for u in live:
        if not re.search(r"PRD\s+§", u["Cites"]) or not re.search(r"TRD\s+§", u["Cites"]):
            rep.fail(f"unit {u['n']}: cites must name a PRD heading and a TRD heading")

    if a.trd:
        trd = md.read(a.trd)
        heads = {t for t, _ in md.sections(trd)}
        ch, crows = md.table(md.section(trd, "4. Component map") or "", ["Component", "Repository", "Folder"])
        folders = {f.rstrip("/") for r in crows for f in re.findall(r"`([^`]+)`", md.cell(r, ch, "Folder"))}
        extra = {"evals/tech", "docs", "features", "tests", "infra", "ops"}
        for u in live:
            for h in cited_headings(u["Cites"], "TRD"):
                if h.strip() and h.strip() not in heads:
                    rep.fail(f"unit {u['n']}: cites TRD §{h.strip()}, which is not a TRD heading")
            b = u["boundary"].rstrip("/")
            if b and folders and not any(b == f or b.startswith(f + "/") for f in folders | extra):
                rep.fail(f"unit {u['n']}: boundary {u['boundary']} is not a folder in the TRD's component map")
        used = {u["boundary"].rstrip("/") for u in live}
        for f in sorted(folders):
            if not any(b == f or b.startswith(f + "/") for b in used):
                rep.warn(f"component folder {f}/ has no unit")

    md.check_placeholders(text, rep, "build plan")
    rep.finish()


if __name__ == "__main__":
    main()
