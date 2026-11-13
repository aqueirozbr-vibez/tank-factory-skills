#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Research gate for docs/research/<brief>.md.

Usage: python3 lint_research.py docs/research/<brief>.md [--mode new|amendment|light]

Checks the discovery stage's code gate: every claim line carries a URL or a
repository path, and the discovery question list is present with at most 10
blocking questions. Also checks the four Discovery building blocks (personas,
today's journey, customer blueprint, competitors and references).
Exit 1 on any FAIL.
"""
import argparse
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

BLOCKS = [
    ("Personas", ["Persona", "Context", "Goal", "pains", "tools", "Frequency", "Source"]),
    ("User journey (today)", ["Step", "Persona", "Action", "Touchpoint", "Pain", "Time", "Source"]),
    ("Customer blueprint", ["Step", "Frontstage", "Backstage", "Support system", "Failure", "Source"]),
    ("Competitors and references", ["Name", "Kind", "Does well", "Gets wrong", "Verdict", "Source"]),
]
VERDICTS = {"adopt", "avoid", "differentiate"}


def sourced(line):
    return md.has_source(line) or bool(re.search(r"\bbrief:\w+", line))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--mode", default=None, choices=["new", "amendment", "light"])
    a = ap.parse_args()
    text = md.read(a.path)
    rep = md.Report("research gate")
    lines = text.splitlines()

    if not lines or not re.match(r"^#\s+Research\s+[—-]\s+\S", lines[0]):
        rep.fail("H1 must be '# Research — <Brief title>' on line 1")
    head = "\n".join(lines[:5])
    mode = a.mode or (re.search(r"mode\s+(new|amendment|light)", head) or [None, "new"])[1]
    if not re.search(r"\b(19|20)\d{2}\b", head):
        rep.fail("byline must carry a date")

    light = mode == "light"
    if md.section(text, "Question tree") is None and not light:
        rep.fail("missing '## Question tree'")

    personas = set()
    for title, cols in BLOCKS:
        body = md.section(text, title)
        if body is None:
            rep.fail(f"missing '## {title}'")
            continue
        if light and re.search(r"no change", body, re.I):
            continue
        hdr, rows = md.table(body, cols)
        if hdr is None:
            rep.fail(f"'{title}': table missing or missing columns {cols}")
            continue
        if not rows:
            rep.fail(f"'{title}': no rows")
        for r in rows:
            name = r[0] if r else "?"
            line = " | ".join(r)
            if not sourced(md.cell(r, hdr, "Source")):
                rep.fail(f"'{title}' row '{name[:40]}': no URL or repository path in Source")
            elif not md.has_source(md.cell(r, hdr, "Source")):
                rep.warn(f"'{title}' row '{name[:40]}': sourced only from the brief — find evidence or ask a non-blocking question")
            for i, c in enumerate(r[:-1]):
                if md.is_empty(c) and not re.search(r"q\d+", c):
                    rep.fail(f"'{title}' row '{name[:40]}': empty cell '{hdr[i]}' — fill it or point to a question id")
            if title == "Personas":
                personas.add(name.strip("*` "))
            if title == "User journey (today)":
                if not re.match(r"^J-\d+$", name.strip("` ")):
                    rep.fail(f"journey step id '{name}' must be J-<n>")
                p = md.cell(r, hdr, "Persona").strip("*` ")
                if personas and p not in personas:
                    rep.fail(f"journey step {name}: persona '{p}' is not in the Personas table")
            if title == "Competitors and references":
                v = md.cell(r, hdr, "Verdict").strip("*` ").lower()
                if v not in VERDICTS:
                    rep.fail(f"competitor '{name[:40]}': verdict '{v}' must be adopt, avoid or differentiate")
                if not re.search(r"https?://", line):
                    rep.fail(f"competitor '{name[:40]}': needs a URL")

    for title, required in (("Constraints", not light), ("Findings", True),
                            ("Repository findings", mode == "amendment")):
        body = md.section(text, title)
        if body is None:
            if required:
                rep.fail(f"missing '## {title}'")
            continue
        for b in md.bullets(body):
            if not sourced(b):
                rep.fail(f"'{title}': claim without a URL or repository path: {b[:70]}")
            elif title == "Repository findings" and not md.has_source(b):
                rep.fail(f"'Repository findings': must cite a path: {b[:70]}")

    body = md.section(text, "Discovery questions")
    if body is None:
        rep.fail("missing '## Discovery questions' (the question list is part of the gate)")
    else:
        hdr, rows = md.table(body, ["ID", "Kind", "Question", "Blocking", "Default"])
        if hdr is None:
            rep.fail("'Discovery questions': table missing columns ID, Kind, Question, Blocking, Default")
        blocking = 0
        for r in rows:
            qid = md.cell(r, hdr, "ID").strip("` ")
            if not re.match(r"^q\d+$", qid):
                rep.fail(f"question id '{qid}' must be q<n>")
            if "?" not in md.cell(r, hdr, "Question"):
                rep.fail(f"{qid}: not phrased as a question")
            if md.cell(r, hdr, "Kind").strip().lower() not in {"product", "technical", "design", "process"}:
                rep.fail(f"{qid}: kind must be product, technical, design or process")
            b = md.cell(r, hdr, "Blocking").strip().lower()
            if b not in {"yes", "no"}:
                rep.fail(f"{qid}: Blocking must be yes or no")
            if b == "yes":
                blocking += 1
            elif md.is_empty(md.cell(r, hdr, "Default")):
                rep.fail(f"{qid}: a non-blocking question needs the default you will assume")
        if blocking > 10:
            rep.fail(f"{blocking} blocking questions; more than 10 returns the brief for narrowing")
        used = set(re.findall(r"→\s*(q\d+)", text))
        listed = {md.cell(r, hdr, "ID").strip("` ") for r in rows} if hdr else set()
        for q in sorted(used - listed):
            rep.fail(f"'{q}' is referenced but missing from the Discovery questions table")

    md.check_placeholders(text, rep, "research")
    rep.finish()


if __name__ == "__main__":
    main()
