#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Conformance-check gate for evals/tech/.

Usage: python3 lint_tech_evals.py --trd docs/trd/<product>.md --root <repository root> [--root <second root>]

Checks that every invariant in TRD §4.1 has its check file under evals/tech/,
that each check carries its header and is not trivially green, that every
component-map folder appears in an import contract, and that the index and
the standards configuration exist. Running the checks is code's job.
Exit 1 on any FAIL.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

TRIVIAL = [r"^\s*assert\s+True\s*$", r"expect\(true\)\.toBe\(true\)", r"^\s*pytest\.skip\(", r"@pytest\.mark\.skip\b",
           r"\b(?:it|test|describe)\.skip\(", r"@pytest\.mark\.xfail", r"\bxit\(", r"\btest\.todo\("]


def find(roots, rel):
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trd", required=True)
    ap.add_argument("--root", action="append", required=True)
    a = ap.parse_args()
    rep = md.Report("tech evals gate")
    trd = md.read(a.trd)
    s4 = md.section(trd, "4. Component map") or ""
    ch, crows = md.table(s4, ["Component", "Repository", "Folder"])
    ih, irows = md.table(md.section(s4, "4.1 Invariants", 3) or "", ["ID", "Invariant", "Check"])
    if not irows:
        rep.fail("TRD §4.1 has no invariants table to check against")
    if not crows:
        rep.fail("TRD §4 has no component map to check against")

    roots = a.root
    evals = [os.path.join(r, "evals", "tech") for r in roots if os.path.isdir(os.path.join(r, "evals", "tech"))]
    if not evals:
        rep.fail("no evals/tech/ directory under any --root")
        rep.finish()

    # Invariants
    for r in irows:
        iid = r[0].strip("*` ")
        paths = re.findall(r"`(evals/tech/[^`]+)`", md.cell(r, ih, "Check"))
        if not paths:
            rep.fail(f"{iid}: TRD names no check path")
        for rel in paths:
            p = find(roots, rel)
            if p is None:
                rep.fail(f"{iid}: check file {rel} does not exist")
                continue
            body = md.read(p)
            if not body.strip():
                rep.fail(f"{iid}: {rel} is empty")
                continue
            if iid not in body:
                rep.fail(f"{iid}: {rel} does not mention {iid}")
            if "/boundaries/" not in rel:
                if not re.search(r"Fails when\s*:", body):
                    rep.fail(f"{iid}: {rel} has no 'Fails when:' line stating the seeded violation")
                if not re.search(r"\bassert\b|expect\(|raise\s+AssertionError|\.should\b", body):
                    rep.fail(f"{iid}: {rel} asserts nothing")
                for pat in TRIVIAL:
                    if re.search(pat, body, re.M):
                        rep.fail(f"{iid}: {rel} is switched off or trivially green ({pat})")

    # Boundaries
    contracts = ""
    for e in evals:
        b = os.path.join(e, "boundaries")
        if os.path.isdir(b):
            for n in sorted(os.listdir(b)):
                contracts += "\n" + md.read(os.path.join(b, n))
    if not contracts.strip():
        rep.fail("evals/tech/boundaries/ holds no import contract")
    for r in crows:
        for folder in re.findall(r"`([^`]+)`", md.cell(r, ch, "Folder")):
            f = folder.strip("/")
            forms = {f, f.replace("/", "."), "^" + f, f + "/"}
            if not any(x in contracts for x in forms):
                rep.fail(f"component '{r[0]}': folder {folder} appears in no import contract")

    # Index and standards
    for e in evals:
        idx = os.path.join(e, "README.md")
        if not os.path.exists(idx):
            rep.fail(f"{e}/README.md (the index) is missing")
        std = os.path.join(e, "standards")
        if not os.path.isdir(std) or not os.listdir(std):
            rep.fail(f"{e}/standards/ holds no lint configuration")
    index = "\n".join(md.read(os.path.join(e, "README.md")) for e in evals if os.path.exists(os.path.join(e, "README.md")))
    if index:
        for r in irows:
            if r[0].strip("*` ") not in index:
                rep.fail(f"index: {r[0]} has no row in evals/tech/README.md")
        for r in crows:
            if r[0].strip("*` ") not in index:
                rep.fail(f"index: component '{r[0]}' has no row in evals/tech/README.md")
    rep.finish()


if __name__ == "__main__":
    main()
