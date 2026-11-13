#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Context gate for context/*.md, AGENTS.md and CLAUDE.md.

Usage: python3 lint_context.py --root <repository root> [--trd docs/trd/<product>.md]
           [--build-plan specs/00-build-plan.md] [--max-tokens 40000]

Checks what the factory's context gate checks: exactly six files; no scaffold
text; architecture.md with a complete stack table, boundaries naming existing
folders and ≥ 4 invariants each mapped to a check in evals/tech/; every
ui-context token row with a value; every code-standards rule naming a stack
noun; the protected-files block generated, not typed; progress-tracker.md
holding only its generated header; AGENTS.md listing the six files in order;
the total under the token cap. Exit 1 on any FAIL.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

SIX = ["project-overview.md", "architecture.md", "ui-context.md", "code-standards.md",
       "ai-workflow-rules.md", "progress-tracker.md"]
TOOLS = {"ruff", "eslint", "mypy", "tsc", "pytest", "vitest", "playwright", "prettier", "black",
         "import-linter", "dependency-cruiser", "typescript-eslint", "pyright", "biome"}
STOP = {"the", "and", "for", "with", "from", "none", "slim", "bookworm", "approved", "registry",
        "example", "com", "latest", "image", "base"}


def scaffold(text, name, rep):
    body = md.strip_code(text)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    for i, ln in enumerate(body.splitlines(), 1):
        for m in re.finditer(r"\[([^\]\n]{2,60})\](?!\()", ln):
            if m.group(1).strip().lower() in {"x", " "} or re.match(r"^\d+$", m.group(1)):
                continue
            rep.fail(f"{name}:{i}: scaffold text [{m.group(1)[:30]}]")
        if re.search(r"\be\.g\.", ln):
            rep.fail(f"{name}:{i}: scaffold text 'e.g.' — state the fact")
    md.check_placeholders(text, rep, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--trd")
    ap.add_argument("--build-plan")
    ap.add_argument("--max-tokens", type=int, default=40000)
    a = ap.parse_args()
    rep = md.Report("context gate")
    ctx = os.path.join(a.root, "context")
    if not os.path.isdir(ctx):
        rep.fail(f"{ctx} does not exist")
        rep.finish()

    present = sorted(os.listdir(ctx))
    for f in SIX:
        if f not in present:
            rep.fail(f"context/{f} is missing")
    for f in present:
        if f not in SIX:
            rep.fail(f"context/{f} does not belong: context/ holds exactly the six files")
    T = {f: md.read(os.path.join(ctx, f)) for f in SIX if f in present}

    total = 0
    for f, t in T.items():
        total += len(t)
        if f != "progress-tracker.md":
            scaffold(t, f, rep)
            if len(t.strip()) < 200:
                rep.fail(f"{f}: nearly empty")
        if re.search(r"[^\x00-\x7F]{12,}", t):
            rep.warn(f"{f}: long non-ASCII run; context files are written in English")

    # AGENTS.md and CLAUDE.md
    agents = os.path.join(a.root, "AGENTS.md")
    if not os.path.exists(agents):
        rep.fail("AGENTS.md is missing at the repository root")
    else:
        at = md.read(agents)
        total += len(at)
        scaffold(at, "AGENTS.md", rep)
        pos = [at.find(f) for f in SIX]
        if -1 in pos:
            rep.fail("AGENTS.md does not list all six context files")
        elif pos != sorted(pos):
            rep.fail("AGENTS.md lists the six files out of order")
    claude = os.path.join(a.root, "CLAUDE.md")
    if not os.path.exists(claude) or md.read(claude).strip() != "@AGENTS.md":
        rep.fail("CLAUDE.md must contain the single line '@AGENTS.md'")
    for r, _, names in os.walk(a.root):
        if "AGENTS.md" in names and os.path.abspath(r) != os.path.abspath(a.root) and "node_modules" not in r:
            nt = md.read(os.path.join(r, "AGENTS.md"))
            total += len(nt)
            scaffold(nt, os.path.relpath(os.path.join(r, "AGENTS.md"), a.root), rep)

    est = total // 4
    if est > a.max_tokens:
        rep.fail(f"context is about {est} tokens; the cap is {a.max_tokens} and no phase will start above it")
    elif est > a.max_tokens * 0.8:
        rep.warn(f"context is about {est} tokens, over 80% of the {a.max_tokens} cap")

    plan = md.read(a.build_plan) if a.build_plan and os.path.exists(a.build_plan) else ""
    trd = md.read(a.trd) if a.trd and os.path.exists(a.trd) else ""
    stack_nouns = set(TOOLS)

    # architecture.md
    arch = T.get("architecture.md", "")
    if arch:
        hdr, rows = md.table(md.section(arch, "Stack") or "", ["Repository", "Language", "Package manager", "Base image"])
        if hdr is None or not rows:
            rep.fail("architecture.md: stack table missing (Repository | Language | Package manager | Base image | Frameworks and libraries)")
        for r in rows:
            for i, c in enumerate(r):
                if md.is_empty(c):
                    rep.fail(f"architecture.md: stack table cell '{hdr[i]}' is empty for {r[0]}")
            for c in r[1:]:
                stack_nouns |= {w for w in re.split(r"[^a-z+#]+", c.lower()) if len(w) > 1 and w not in STOP}
        bh, brows = md.table(md.section(arch, "Boundaries") or "", ["Boundary", "Folder", "Responsibility"])
        if bh is None or not brows:
            rep.fail("architecture.md: boundaries table missing (Boundary | Folder | Responsibility | May import | Never imports)")
        for r in brows:
            fs = re.findall(r"`([^`]+)`", md.cell(r, bh, "Folder"))
            if not fs:
                rep.fail(f"architecture.md: boundary '{r[0]}' names no folder")
            for f in fs:
                if not os.path.isdir(os.path.join(a.root, f)) and f.rstrip("/") not in plan and f not in plan:
                    rep.fail(f"architecture.md: boundary '{r[0]}' folder {f} exists neither in the repository nor in the build plan")
        ih, irows = md.table(md.section(arch, "Invariants") or "", ["ID", "Invariant", "Check"])
        if ih is None:
            rep.fail("architecture.md: invariants table missing (ID | Invariant | Check)")
        elif len(irows) < 4:
            rep.fail(f"architecture.md: {len(irows)} invariants; the gate needs ≥ 4")
        for r in irows:
            checks = re.findall(r"`(evals/tech/[^`]+)`", md.cell(r, ih, "Check"))
            if not checks:
                rep.fail(f"architecture.md: {r[0]} maps to no check under evals/tech/")
            for c in checks:
                if not os.path.exists(os.path.join(a.root, c)):
                    rep.fail(f"architecture.md: {r[0]} check {c} does not exist")
        if trd:
            th, trows = md.table(md.section(md.section(trd, "4. Component map") or "", "4.1 Invariants", 3) or "", ["ID", "Invariant", "Check"])
            have = {r[0].strip("*` ") for r in irows}
            for r in trows:
                if r[0].strip("*` ") not in have:
                    rep.fail(f"architecture.md: TRD invariant {r[0]} is missing")

    # ui-context.md
    ui = T.get("ui-context.md", "")
    if ui and not re.search(r"^No UI\b", ui.strip().split("\n", 2)[-1] if ui.startswith("#") else ui, re.M):
        hdr, rows = md.table(md.section(ui, "Tokens") or "", ["Token", "Value", "Use"])
        if hdr is None or not rows:
            rep.fail("ui-context.md: tokens table missing (Token | Value | Use), or write 'No UI: product kind service.'")
        for r in rows:
            if md.is_empty(md.cell(r, hdr, "Value"), allow=("none",)):
                rep.fail(f"ui-context.md: token '{r[0]}' has no value")

    # code-standards.md
    cs = T.get("code-standards.md", "")
    if cs:
        hdr, rows = md.table(md.section(cs, "Rules") or "", ["Rule", "Applies to", "Enforced by"])
        if hdr is None or not rows:
            rep.fail("code-standards.md: rules table missing (Rule | Applies to | Enforced by)")
        for r in rows:
            line = " ".join(r).lower()
            if not any(re.search(r"(?<![a-z])" + re.escape(n) + r"(?![a-z])", line) for n in stack_nouns):
                rep.fail(f"code-standards.md: rule '{r[0][:50]}' names no stack noun — say which language, library or tool")
            if md.is_empty(md.cell(r, hdr, "Enforced by")):
                rep.fail(f"code-standards.md: rule '{r[0][:50]}' is enforced by nothing")

    # ai-workflow-rules.md
    wf = T.get("ai-workflow-rules.md", "")
    if wf:
        m = re.search(r"<!--\s*factory:generated protected-files\s*-->(.*?)<!--\s*/factory:generated\s*-->", wf, re.S)
        if not m:
            rep.fail("ai-workflow-rules.md: the generated protected-files block is missing")
        vc = md.section(wf, "Verification checklist")
        if vc is None:
            rep.fail("ai-workflow-rules.md: '## Verification checklist' missing")
        elif trd:
            pm = re.search(r"```json\s+stack_profile\s*\n(.*?)\n```", trd, re.S)
            if pm:
                import json
                try:
                    for repo in json.loads(pm.group(1)).get("repositories", []):
                        for k in ("format", "lint", "typecheck", "test"):
                            cmd = repo.get("quality", {}).get(k)
                            if cmd and cmd not in vc:
                                rep.fail(f"ai-workflow-rules.md: the checklist does not name `{cmd}` ({repo.get('repository')} {k})")
                except ValueError:
                    rep.warn("TRD stack_profile block is not valid JSON; quality commands not cross-checked")
        us = md.section(wf, "Units and specs")
        if us is None:
            rep.fail("ai-workflow-rules.md: '## Units and specs' missing — say that every unit is built only from its approved spec")
        else:
            for needle, what in (("specs/00-build-plan.md", "the build plan path"), ("specs/<task>-<slug>.md", "where a unit's spec lives"),
                                 ("approv", "that the spec is approved before any code"), ("spec_defect", "what to do with a spec that cannot be built")):
                if needle not in us:
                    rep.fail(f"ai-workflow-rules.md: '## Units and specs' does not state {what} (`{needle}`)")
        if not re.search(r"context_conflict", wf) or not re.search(r"discovery note", wf, re.I):
            rep.fail("ai-workflow-rules.md: must say what to do on a context_conflict and when to record a discovery note")

    # progress-tracker.md
    pt = T.get("progress-tracker.md")
    if pt is not None:
        rest = re.sub(r"<!--.*?-->", "", pt, flags=re.S)
        rest = "\n".join(l for l in rest.splitlines() if l.strip() and not l.startswith("# "))
        if "factory:generated progress-tracker" not in pt:
            rep.fail("progress-tracker.md: the generated header is missing")
        if rest.strip():
            rep.fail("progress-tracker.md: holds content besides its generated header; code renders the tracker")

    # project-overview.md
    po = T.get("project-overview.md", "")
    if po:
        for s in ("Product", "Users and roles", "Features", "Scope", "Principles", "Glossary"):
            if md.section(po, s) is None:
                rep.fail(f"project-overview.md: '## {s}' missing")
    rep.finish()


if __name__ == "__main__":
    main()
