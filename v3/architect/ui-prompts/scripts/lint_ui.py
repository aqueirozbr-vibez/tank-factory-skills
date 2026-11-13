#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Branding gate for docs/design/ui-prompts.md and docs/design/styleguide.md.

Usage: python3 lint_ui.py docs/design/ui-prompts.md docs/design/styleguide.md
                          --prd docs/prd/<product>.md [--features features]

Checks the four UI building blocks: design system (complete token table,
open-source fonts and icons), key screens (one prompt per PRD screen id),
mobile view (breakpoints and a mobile line per screen) and component states.
Exit 1 on any FAIL.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

SCREEN = r"\b[A-Z]{1,3}-\d{2,3}\b"
CATEGORIES = {"colour": "colour", "color": "colour", "type": "type", "typography": "type",
              "spacing": "spacing", "space": "spacing", "radius": "radius",
              "elevation": "elevation", "shadow": "elevation", "motion": "motion"}
OPEN = re.compile(r"OFL|SIL|Apache|MIT|ISC|CC0|CC-BY|BSD|MPL|Unlicense|system", re.I)
BASE_STATES = {"default", "hover", "focus", "disabled"}
LABELS = ["Purpose", "Roles", "Shows", "Actions", "Layout", "Mobile view", "States", "Prompt"]


def prd_screens(path):
    text = md.read(path)
    hdr, rows = md.table(md.section(text, "Journeys and screens") or "", ["Screen", "Name", "Purpose"])
    fields = set()
    for _, b in md.sections(md.section(text, "Objects") or "", 3):
        fh, frows = md.table(b, ["Field", "Type"])
        fields |= {r[0].strip("*` ") for r in frows}
    return {r[0].strip("*` "): md.cell(r, hdr, "Name") for r in rows}, fields


def prd_personas(path):
    hdr, rows = md.table(md.section(md.read(path), "Users and personas") or "", ["Persona", "Who"])
    return [r[0].strip("*` ") for r in rows]


def styleguide(text, rep):
    comps, states = {}, {}
    th, trows = md.table(md.section(text, "Tokens") or "", ["Token", "Category", "Value", "Use"])
    if th is None or not trows:
        rep.fail("styleguide: '## Tokens' table missing (Token | Category | Value | Use)")
    seen = set()
    for r in trows:
        tok = r[0].strip("*` ")
        if md.is_empty(md.cell(r, th, "Value"), allow=("none",)):
            rep.fail(f"styleguide: token '{tok}' has no value")
        if not re.match(r"^[a-z][a-z0-9]*(\.[a-z0-9-]+)+$", tok):
            rep.fail(f"styleguide: token '{tok}' must be dotted lowercase (color.primary)")
        c = CATEGORIES.get(md.cell(r, th, "Category").strip("*` ").lower())
        if c is None:
            rep.fail(f"styleguide: token '{tok}' has an unknown category '{md.cell(r, th, 'Category')}'")
        seen.add(c)
    for need in sorted(set(CATEGORIES.values()) - seen):
        if trows:
            rep.fail(f"styleguide: no token in category '{need}'")

    fh, frows = md.table(md.section(text, "Fonts and icons") or "", ["Asset", "Family", "License"])
    if fh is None or not frows:
        rep.fail("styleguide: '## Fonts and icons' table missing (Asset | Family | License)")
    for r in frows:
        if not OPEN.search(md.cell(r, fh, "License")):
            rep.fail(f"styleguide: '{md.cell(r, fh, 'Family')}' licence '{md.cell(r, fh, 'License')}' is not an open-source licence")

    bh, brows = md.table(md.section(text, "Breakpoints") or "", ["Name", "Min width", "Layout"])
    if bh is None or len(brows) < 2:
        rep.fail("styleguide: '## Breakpoints' needs ≥ 2 rows (Name | Min width | Layout change)")
    widths = [int(m.group(1)) for r in brows for m in [re.search(r"(\d+)", md.cell(r, bh, "Min width"))] if m]
    if brows and not any(w <= 480 for w in widths):
        rep.fail("styleguide: no breakpoint at ≤ 480 px, so the mobile view is undefined")

    ch, crows = md.table(md.section(text, "Components") or "", ["Component", "Use", "Interactive"])
    if ch is None or not crows:
        rep.fail("styleguide: '## Components' table missing (Component | Use | Interactive)")
    for r in crows:
        comps[r[0].strip("*` ")] = md.cell(r, ch, "Interactive").strip().lower().startswith("y")

    sh, srows = md.table(md.section(text, "Component states") or "", ["Component", "State", "Appearance", "Message"])
    if sh is None or not srows:
        rep.fail("styleguide: '## Component states' table missing (Component | State | Appearance | Message)")
    for r in srows:
        c, s = r[0].strip("*` "), md.cell(r, sh, "State").strip("*` ").lower()
        states.setdefault(c, set()).add(s)
        if c not in comps:
            rep.fail(f"styleguide: state row for '{c}', which is not in Components")
        if md.is_empty(md.cell(r, sh, "Appearance")):
            rep.fail(f"styleguide: {c} / {s} has no appearance")
        if s == "error" and md.is_empty(md.cell(r, sh, "Message")):
            rep.fail(f"styleguide: {c} / error has no message text")
    for c, interactive in comps.items():
        missing = BASE_STATES - states.get(c, set()) if interactive else set()
        if missing:
            rep.fail(f"styleguide: interactive component '{c}' lacks states {sorted(missing)}")
    return comps, states


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ui_prompts")
    ap.add_argument("styleguide")
    ap.add_argument("--prd", required=True)
    ap.add_argument("--features")
    a = ap.parse_args()
    rep = md.Report("branding gate")
    ui, sg = md.read(a.ui_prompts), md.read(a.styleguide)
    screens, fields = prd_screens(a.prd)
    if not screens:
        rep.fail("the PRD names no screens; branding runs only when it does")
    comps, states = styleguide(sg, rep)

    if not re.match(r"^#\s+UI brief\s+[—-]\s+\S", ui.splitlines()[0] if ui else ""):
        rep.fail("ui-prompts: H1 must be '# UI brief — <Product name>'")

    personas = prd_personas(a.prd)
    j = md.section(ui, "Journey maps")
    if j is None:
        rep.fail("ui-prompts: missing '## Journey maps'")
    else:
        used, mapped = set(), set()
        cols = ["Step", "Stage", "Screen", "Action", "Result", "Feeling", "Pain point", "Design response", "Next"]
        for title, body in md.sections(j, 3):
            who = next((p for p in personas if title.strip().startswith(p)), None)
            if who is None:
                rep.fail(f"ui-prompts: journey map '{title}' is for no persona in the PRD")
                continue
            mapped.add(who)
            hdr, rows = md.table(body, cols)
            if hdr is None or not rows:
                rep.fail(f"ui-prompts: journey map '{title}' needs a table ({' | '.join(cols)})")
                continue
            for r in rows:
                step = r[0].strip("*` ")
                for sid in re.findall(SCREEN, md.cell(r, hdr, "Screen")):
                    used.add(sid)
                    if sid not in screens:
                        rep.fail(f"ui-prompts: journey step names {sid}, which is not in the PRD's screens map")
                if md.is_empty(md.cell(r, hdr, "Stage")):
                    rep.fail(f"ui-prompts: journey map '{title}' step {step}: no stage")
                m = re.match(r"^\s*([+\-−]?)([0-2])\b", md.cell(r, hdr, "Feeling"))
                if not m:
                    rep.fail(f"ui-prompts: journey map '{title}' step {step}: feeling must start with a score from -2 to +2")
                elif m.group(1) in "-−" and m.group(1) and int(m.group(2)) >= 1:
                    for c in ("Pain point", "Design response"):
                        if md.is_empty(md.cell(r, hdr, c)):
                            rep.fail(f"ui-prompts: journey map '{title}' step {step}: a negative feeling needs a {c.lower()}")
        for who in personas:
            if who not in mapped:
                rep.fail(f"ui-prompts: persona '{who}' has no journey map")
        for sid in sorted(set(screens) - used):
            rep.fail(f"ui-prompts: screen {sid} appears in no journey map")

    p = md.section(ui, "Screen prompts")
    if p is None:
        rep.fail("ui-prompts: missing '## Screen prompts'")
    else:
        got = {}
        for t, b in md.sections(p, 3):
            m = re.match(r"^(" + SCREEN[2:-2] + r")\s+[—-]\s+\S", t)
            if not m:
                rep.fail(f"ui-prompts: prompt heading '### {t}' must be '### <id> — <Name>'")
                continue
            got[m.group(1)] = b
        for sid in sorted(set(screens) - set(got)):
            rep.fail(f"ui-prompts: no screen prompt for {sid}")
        for sid in sorted(set(got) - set(screens)):
            rep.fail(f"ui-prompts: prompt for {sid}, which is not in the PRD's screens map")
        for sid, b in got.items():
            for lab in LABELS:
                v = md.labelled(b, lab)
                if v is None or md.is_empty(v):
                    rep.fail(f"ui-prompts {sid}: '{lab}:' line missing or empty")
            mv = md.labelled(b, "Mobile view") or ""
            if mv and not re.search(r"\d", mv):
                rep.warn(f"ui-prompts {sid}: mobile view names no breakpoint or size")
            st = md.labelled(b, "States") or ""
            for part in [x for x in st.split(";") if ":" in x]:
                c, lst = part.split(":", 1)
                c = c.strip("*` ")
                if comps and c not in comps:
                    rep.fail(f"ui-prompts {sid}: component '{c}' is not in the styleguide's Components")
                for s in [x.strip("*` .").lower() for x in lst.split(",") if x.strip()]:
                    if c in states and s not in states[c]:
                        rep.fail(f"ui-prompts {sid}: state '{c}: {s}' is not in the styleguide's Component states")

    s = md.section(ui, "UI scenarios")
    if s is None:
        rep.fail("ui-prompts: missing '## UI scenarios'")
    else:
        hdr, rows = md.table(s, ["Screen", "Scenario", "Feature file"])
        covered = {sid for r in rows for sid in re.findall(SCREEN, md.cell(r, hdr, "Screen"))} if hdr else set()
        for sid in sorted(set(screens) - covered):
            rep.fail(f"ui-prompts: screen {sid} has no UI scenario")
        if a.features and hdr:
            for r in rows:
                f = md.cell(r, hdr, "Feature file").strip("` ")
                path = os.path.join(os.path.dirname(a.features.rstrip("/")) or ".", f)
                if not os.path.exists(path):
                    rep.fail(f"ui-prompts: feature file {f} does not exist")
                elif md.cell(r, hdr, "Scenario").strip() not in md.read(path):
                    rep.fail(f"ui-prompts: scenario '{md.cell(r, hdr, 'Scenario')}' is not in {f}")

    md.check_placeholders(ui, rep, "ui-prompts")
    md.check_placeholders(sg, rep, "styleguide")
    rep.finish()


if __name__ == "__main__":
    main()
