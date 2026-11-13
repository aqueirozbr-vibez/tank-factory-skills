#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Self-test for the Architect skills' lint scripts.

Every lint must pass on the exemplar product (examples/reading-capture) and fail,
with the expected message, on a seeded violation — the same proof the factory
asks of a project's quality commands. Run: python3 selftest.py
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).parent
E = ROOT / "examples" / "reading-capture"
A = ROOT / "architect"
PRD, TRD, RES = E / "docs/prd/reading-capture.md", E / "docs/trd/reading-capture.md", E / "docs/research/reading-capture.md"
SG, UI, WF = E / "docs/design/styleguide.md", E / "docs/design/ui-prompts.md", E / "docs/design/wireframes"
PLAN, ENV = E / "specs/00-build-plan.md", E / "factory-config/environment.yaml"
TMP = pathlib.Path(tempfile.mkdtemp(prefix="tf-selftest-"))
results = []


def run(name, args, expect_fail=None):
    p = subprocess.run([sys.executable] + [str(a) for a in args], capture_output=True, text=True)
    ok = (p.returncode == 0) if expect_fail is None else (p.returncode == 1 and expect_fail in p.stdout)
    results.append((ok, name, "" if ok else p.stdout.strip()[-400:] + p.stderr.strip()[-300:]))


def mutated(src, *pairs, name=None):
    t = pathlib.Path(src).read_text()
    for a, b in pairs:
        assert a in t, f"selftest mutation target missing in {src}: {a[:50]}"
        t = t.replace(a, b)
    out = TMP / (name or ("bad-" + pathlib.Path(src).name))
    out.write_text(t)
    return out


def tree(src, name):
    d = TMP / name
    shutil.copytree(src, d)
    return d


L = lambda skill, script: A / skill / "scripts" / script

# product-research
run("research: exemplar passes", [L("product-research", "lint_research.py"), RES])
run("research: unsourced claim fails", [L("product-research", "lint_research.py"),
    mutated(RES, (" — https://example.com/it/coverage-survey", ""))], "claim without a URL")
# prd
run("prd: exemplar passes", [L("prd", "lint_prd.py"), PRD, "--research", RES])
run("prd: support system missing from the service blueprint fails", [L("prd", "lint_prd.py"),
    mutated(PRD, ("| B-1 | S-01 | Inspector opens the app; today's assets are already on the phone | The asset mirror is refreshed nightly, read-only | Asset Registry |",
                  "| B-1 | S-01 | Inspector opens the app; today's assets are already on the phone | The asset mirror is refreshed nightly, read-only | none |")),
    "--research", RES], "from the research blueprint is on no step")
run("prd: screen off every Screens: line fails", [L("prd", "lint_prd.py"),
    mutated(PRD, ("\nScreens: S-02\n", "\n"))], "is on no capability's 'Screens:' line")
run("prd: principle without a check fails", [L("prd", "lint_prd.py"),
    mutated(PRD, ("| conformance check: every reading the API acknowledges has a stored row |", "| — |"))], "no compliance check")
# po-evals
F = L("po-evals", "lint_features.py")
run("features: exemplar passes with bindings", [F, E / "features", "--prd", PRD, "--bindings", E / "holdout/tests/acceptance/features"])
bad = tree(E / "features", "bad-features")
p = bad / "anomaly-review/review-queue.feature"
p.write_text(p.read_text().replace("  @SC-6\n", ""))
run("features: untagged scenario fails", [F, bad, "--prd", PRD], "has no @SC-n or @AC-n tag")
# ui-prompts
U = L("ui-prompts", "lint_ui.py")
run("ui: exemplar passes", [U, UI, SG, "--prd", PRD, "--features", E / "features"])
run("ui: empty token value fails", [U, UI, mutated(SG, ("| color.warn | colour | #7a5200 |", "| color.warn | colour |  |")), "--prd", PRD], "has no value")
run("ui: negative journey step without a design response fails", [U, mutated(UI, ("| Not knowing whether a reading was lost | The Unsent badge and its sentence say the reading is safe on the phone |", "| Not knowing whether a reading was lost | — |")), SG, "--prd", PRD], "a negative feeling needs a design response")
run("ui: missing screen prompt fails", [U, mutated(UI, ("### S-02 — Review Queue", "### S-09 — Review Queue")), SG, "--prd", PRD], "no screen prompt for S-02")
# wireframes
W = L("wireframes", "lint_wireframes.py")
wargs = ["--prd", PRD, "--styleguide", SG, "--ui-prompts", UI]
run("wireframes: exemplar passes", [W, WF] + wargs)
bad = tree(WF, "bad-wireframes")
p = bad / "s-01-reading-capture.html"
p.write_text(p.read_text().replace("<title>", '<link rel="stylesheet" href="https://fonts.example/inter.css"><title>'))
run("wireframes: external reference fails", [W, bad] + wargs, "external reference")
# trd
T = L("trd", "lint_trd.py")
run("trd: exemplar passes", [T, TRD, "--prd", PRD, "--research", RES])
run("trd: untyped endpoint fails", [T, mutated(TRD, ("| `DecisionIn` | `AnomalyOut` |", "| JSON | object |")), "--prd", PRD], "every endpoint is typed")
run("trd: invariant without a check fails", [T, mutated(TRD, ("`evals/tech/invariants/test_inv_4_revision_on_correction.py`", "unit tests")), "--prd", PRD], "names no check file")
# stack-profile
S = L("stack-profile", "lint_stack_profile.py")
run("stack: exemplar passes", [S, TRD, "--guardrails", ENV, "--prd", PRD, "--new-product"])
run("stack: image outside the guardrails fails", [S, mutated(TRD, ("registry.example/approved/python:3.12-slim", "docker.io/library/python:3.12-slim")),
    "--guardrails", ENV, "--prd", PRD], "not from an allowed source")
run("stack: unsupported stack fails", [S, mutated(TRD, ('"typescript@5.6"', '"rust@1.82"')), "--guardrails", ENV], "is not a supported stack")
# tech-lead-evals
V = L("tech-lead-evals", "lint_tech_evals.py")
run("tech evals: exemplar passes", [V, "--trd", TRD, "--root", E])
bad = TMP / "bad-evals-root"
shutil.copytree(E / "evals", bad / "evals")
(bad / "evals/tech/invariants/test_inv_2_idempotent_write.py").unlink()
run("tech evals: missing check fails", [V, "--trd", TRD, "--root", bad], "does not exist")
# context-build
C = L("context-build", "lint_context.py")
run("context: exemplar passes", [C, "--root", E, "--trd", TRD, "--build-plan", PLAN])
bad = TMP / "bad-context-root"
for d in ("context", "evals"):
    shutil.copytree(E / d, bad / d)
for f in ("AGENTS.md", "CLAUDE.md"):
    shutil.copy(E / f, bad / f)
p = bad / "context/code-standards.md"
p.write_text(p.read_text().replace("| No magic numbers | Python | ruff `PLR2004` |", "| Write clean code | everything | reviewers |"))
p = bad / "context/progress-tracker.md"
p.write_text(p.read_text() + "\n- Unit 1 done\n")
run("context: generic rule fails", [C, "--root", bad, "--build-plan", PLAN], "names no stack noun")
run("context: hand-written tracker fails", [C, "--root", bad, "--build-plan", PLAN], "besides its generated header")
p = bad / "context/ai-workflow-rules.md"
p.write_text(p.read_text().replace("## Units and specs", "## Units"))
run("context: missing units-and-specs rule fails", [C, "--root", bad, "--build-plan", PLAN], "Units and specs' missing")
# build-plan
B = L("build-plan", "lint_build_plan.py")
run("plan: exemplar passes", [B, PLAN, "--prd", PRD, "--trd", TRD])
run("plan: cycle fails", [B, mutated(PLAN, ("- Depends on: 1, 2\n", "- Depends on: 1, 4\n")), "--prd", PRD, "--trd", TRD], "dependency cycle")
run("plan: uncovered requirement fails", [B, mutated(PLAN, ("(FR-2.2)", ""), name="bad-plan2.md"), "--prd", PRD, "--trd", TRD], "FR-2.2 is carried by no unit")

shutil.rmtree(TMP, ignore_errors=True)
for ok, name, out in results:
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "\n      " + out.replace("\n", "\n      ")))
bad = [r for r in results if not r[0]]
print(f"\n{len(results) - len(bad)} of {len(results)} self-tests passed")
sys.exit(1 if bad else 0)
