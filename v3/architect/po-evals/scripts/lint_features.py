#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Feature-file gate for features/**/*.feature.

Usage: python3 lint_features.py features --prd docs/prd/<product>.md
                                [--bindings <holdout>/tests/acceptance/features]

Checks that every file parses as Gherkin, every scenario carries @SC-n or
@AC-n, every PRD success criterion has ≥ 1 scenario, every PRD feature slug
has its file, UI scenarios name an existing screen, and — with --bindings —
that every non-manual scenario has a binding. Whether a binding fails on
`main` is checked by running it, which code does. Exit 1 on any FAIL.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

STEP = re.compile(r"^(Given|When|Then|And|But|\*)\s+\S")


def parse(path, rep):
    """Return (feature_name, [scenario dicts]); report syntax problems."""
    name, scenarios, pending, cur, outline_open = None, [], [], None, False
    feature_tags = []
    in_doc = False
    for n, raw in enumerate(md.read(path).splitlines(), 1):
        ln = raw.strip()
        if ln.startswith('"""') or ln.startswith("```"):
            in_doc = not in_doc
            continue
        if in_doc or not ln or ln.startswith("#") or ln.startswith("|"):
            continue
        if ln.startswith("@"):
            pending += ln.split()
            continue
        m = re.match(r"^(Feature|Background|Rule|Scenario Outline|Scenario Template|Scenario|Example|Examples|Scenarios)\s*:\s*(.*)$", ln)
        if m:
            kw, title = m.group(1), m.group(2).strip()
            if kw == "Feature":
                if name is not None:
                    rep.fail(f"{path}:{n}: more than one Feature in the file")
                name, feature_tags, pending = title, pending, []
                if not title:
                    rep.fail(f"{path}:{n}: Feature has no name")
            elif kw in ("Scenario", "Example", "Scenario Outline", "Scenario Template"):
                cur = {"name": title, "tags": feature_tags + pending, "own_tags": pending, "steps": [],
                       "line": n, "outline": kw.startswith("Scenario O") or kw.startswith("Scenario T"),
                       "examples": False}
                scenarios.append(cur)
                pending = []
                if not title:
                    rep.fail(f"{path}:{n}: scenario has no name")
            elif kw in ("Examples", "Scenarios"):
                if cur is None or not cur["outline"]:
                    rep.fail(f"{path}:{n}: Examples outside a Scenario Outline")
                else:
                    cur["examples"] = True
                pending = []
            elif kw == "Background":
                cur = {"name": "Background", "tags": [], "own_tags": [], "steps": [], "line": n,
                       "outline": False, "examples": False, "background": True}
                pending = []
            else:
                pending = []
            continue
        if STEP.match(ln):
            if cur is None:
                rep.fail(f"{path}:{n}: step before any Scenario")
            else:
                cur["steps"].append(ln)
            continue
        if name is not None and cur is None:
            continue  # free-text description under Feature
        if cur is not None and not cur["steps"]:
            continue  # description under a scenario
        rep.fail(f"{path}:{n}: not Gherkin: {ln[:60]}")
    if name is None:
        rep.fail(f"{path}: no 'Feature:' line")
    for s in scenarios:
        kinds, last = [], None
        for st in s["steps"]:
            k = st.split()[0]
            last = k if k in ("Given", "When", "Then") else last
            if last is None:
                rep.fail(f"{path}:{s['line']}: '{s['name']}' starts with {k}")
            kinds.append(last)
        if "When" not in kinds or "Then" not in kinds:
            rep.fail(f"{path}:{s['line']}: '{s['name']}' needs a When and a Then")
        order = [k for i, k in enumerate(kinds) if k and (i == 0 or kinds[i - 1] != k)]
        if order != sorted(order, key=["Given", "When", "Then"].index):
            rep.fail(f"{path}:{s['line']}: '{s['name']}' steps are not in Given → When → Then order")
        if s["outline"] and not s["examples"]:
            rep.fail(f"{path}:{s['line']}: Scenario Outline '{s['name']}' has no Examples")
        for st in s["steps"]:
            if re.search(r"(#[a-z][\w-]+\b|\bxpath\b|data-testid|\.[a-z]+-[a-z-]+\b|https?://)", st):
                rep.warn(f"{path}:{s['line']}: step holds a selector or URL; keep those in the binding: {st[:60]}")
    names = [s["name"] for s in scenarios]
    for d in sorted({x for x in names if names.count(x) > 1}):
        rep.fail(f"{path}: scenario name used twice: '{d}'")
    return name, scenarios


def prd_facts(path):
    text = md.read(path)
    feats = {}
    for t, b in md.sections(text):
        m = re.match(r"^Capability\s+\d+\s+[—-]\s+(.+)$", t)
        if m:
            for f in re.findall(r"^\s*[-*]\s+`([a-z0-9][a-z0-9-]*)`\s+[—-]", b, re.M):
                feats[f] = md.slug(m.group(1))
    scs = set(re.findall(r"^\s*[-*]\s+(SC-\d+)\b[^:\n]*:", text, re.M))
    owner = dict(re.findall(r"^\s*[-*]\s+(SC-\d+)\s*\(`([a-z0-9-]+)`\)\s*:", text, re.M))
    js = md.section(text, "Journeys and screens") or ""
    hdr, rows = md.table(js, ["Screen", "Name", "Purpose"])
    screens = {r[0].strip("*` ") for r in rows}
    return feats, scs, screens, owner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("features")
    ap.add_argument("--prd", required=True)
    ap.add_argument("--bindings")
    a = ap.parse_args()
    rep = md.Report("feature gate")
    feats, scs, screens, owner = prd_facts(a.prd)

    files = []
    for root, _, names in os.walk(a.features):
        files += [os.path.join(root, n) for n in names if n.endswith(".feature")]
    if not files:
        rep.fail(f"no .feature files under {a.features}")

    seen_sc, found, bound_sc = set(), {}, set()
    for path in sorted(files):
        rel = os.path.relpath(path, a.features).replace(os.sep, "/")
        fname, scenarios = parse(path, rep)
        found[rel] = scenarios
        cap, stem = os.path.dirname(rel), os.path.basename(rel)[:-len(".feature")]
        if fname and md.slug(fname) != stem:
            rep.fail(f"{rel}: Feature is named '{fname}'; name it as its slug in words ('{stem.replace('-', ' ').capitalize()}')")
        ftags = scenarios[0]["tags"][:len(scenarios[0]["tags"]) - len(scenarios[0]["own_tags"])] if scenarios else []
        if scenarios and f"@capability-{cap}" not in ftags:
            rep.fail(f"{rel}: the Feature line needs the tag @capability-{cap}")
        if not scenarios:
            rep.fail(f"{rel}: no scenarios")
        for s in scenarios:
            tags = s["tags"]
            sc = [t[1:] for t in tags if re.match(r"^@SC-\d+$", t)]
            ac = [t for t in tags if re.match(r"^@AC-\d+$", t)]
            if not sc and not ac:
                rep.fail(f"{rel}:{s['line']}: '{s['name']}' has no @SC-n or @AC-n tag")
            for x in sc:
                if scs and x not in scs:
                    rep.fail(f"{rel}:{s['line']}: @{x} is not a success criterion in the PRD")
                elif x in owner and owner[x] != stem:
                    rep.fail(f"{rel}:{s['line']}: @{x} belongs to feature `{owner[x]}`; a scenario is tagged with a criterion of its own feature")
                else:
                    seen_sc.add(x)
                    if "@manual" not in tags:
                        bound_sc.add(x)
            scr = [t[len("@screen-"):] for t in tags if t.startswith("@screen-")]
            if "@ui" in tags and not scr:
                rep.fail(f"{rel}:{s['line']}: '{s['name']}' is @ui but names no @screen-<id>")
            for x in scr:
                if screens and x not in screens:
                    rep.fail(f"{rel}:{s['line']}: @screen-{x} is not in the PRD's screens map")

    for f, cap in sorted(feats.items()):
        if f"{cap}/{f}.feature" not in found:
            rep.fail(f"PRD feature `{f}` has no file features/{cap}/{f}.feature")
    for rel in found:
        stem = os.path.basename(rel)[:-len(".feature")]
        if feats and stem not in feats:
            rep.fail(f"{rel}: no feature `{stem}` in the PRD")
    for x in sorted(scs - seen_sc, key=lambda s: int(s.split("-")[1])):
        rep.fail(f"{x} has no scenario in its own feature file")
    for x in sorted(seen_sc - bound_sc, key=lambda s: int(s.split("-")[1])):
        rep.warn(f"{x} is checked only by @manual scenarios; add a bound scenario unless only a person can judge it")

    if a.bindings:
        for rel, scenarios in found.items():
            stem = rel[:-len(".feature")]
            cands = [p for p in _walk(a.bindings) if _norm(os.path.relpath(p, a.bindings)) == _norm(rel)]
            body = "\n".join(md.read(p) for p in cands)
            need = [s for s in scenarios if "@manual" not in s["tags"]]
            if need and not cands:
                rep.fail(f"{rel}: no binding file at the mirrored path under {a.bindings}")
                continue
            for s in need:
                if s["name"] not in body:
                    rep.fail(f"{rel}: scenario '{s['name']}' has no binding carrying its name")
                for t in [t for t in s["tags"] if re.match(r"^@(SC|AC)-\d+$", t)]:
                    if t[1:] not in body and t[1:].replace("-", "_") not in body:
                        rep.fail(f"{rel}: binding for '{s['name']}' does not carry {t}")
            for m in re.finditer(r"^\s*(?:from|import)\s+['\"]?(\.\./\.\./\.\./|src/|apps/|packages/)|from\s+(src|apps|app)\b", body, re.M):
                rep.fail(f"{rel}: binding imports product source ('{m.group(0).strip()[:40]}'); bind through the public interface")
    else:
        n = sum(1 for sc in found.values() for s in sc if "@manual" not in s["tags"])
        rep.warn(f"bindings not checked: {n} non-manual scenarios need one (pass --bindings once a stack profile exists)")
    rep.finish()


def _norm(rel):
    """Feature or binding path reduced to capability/feature, dashes and underscores alike."""
    d, base = os.path.split(rel.replace(os.sep, "/"))
    base = re.sub(r"^test_|(\.spec|\.test|_test|\.steps)?\.[a-z]+$", "", base)
    return (d + "/" + base).replace("-", "_").lower()


def _walk(root):
    for r, _, names in os.walk(root):
        for n in names:
            yield os.path.join(r, n)


if __name__ == "__main__":
    main()
