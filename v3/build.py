#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Sync shared files into each skill, copy exemplars, and write skills.lock.example.

Run from the package root after any edit: python3 build.py
"""
import hashlib
import pathlib
import shutil

ROOT = pathlib.Path(__file__).parent
EX = ROOT / "examples" / "reading-capture"
SK = ROOT / "architect"

COPIES = {
    "product-research": [("docs/research/reading-capture.md", "exemplar.md")],
    "prd": [("docs/prd/reading-capture.md", "exemplar.md")],
    "po-evals": [("features", "exemplar/features"), ("holdout/tests/acceptance/features", "exemplar/bindings")],
    "ui-prompts": [("docs/design/ui-prompts.md", "exemplar-ui-prompts.md"), ("docs/design/styleguide.md", "exemplar-styleguide.md")],
    "wireframes": [("docs/design/wireframes", "exemplar")],
    "trd": [("docs/trd/reading-capture.md", "exemplar.md")],
    "stack-profile": [("factory-config/environment.yaml", "environment.example.yaml")],
    "tech-lead-evals": [("evals/tech", "exemplar")],
    "context-build": [("context", "exemplar/context"), ("AGENTS.md", "exemplar/AGENTS.example.md"), ("CLAUDE.md", "exemplar/CLAUDE.example.md")],
    "build-plan": [("specs/00-build-plan.md", "exemplar.md")],
}


def main():
    lock = []
    for skill in sorted(p.name for p in SK.iterdir() if p.is_dir()):
        d = SK / skill
        shutil.copy(ROOT / "shared" / "_md.py", d / "scripts" / "_md.py")
        for src, dst in COPIES.get(skill, []):
            s, t = EX / src, d / "references" / dst
            if t.exists():
                shutil.rmtree(t) if t.is_dir() else t.unlink()
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(s, t, ignore=shutil.ignore_patterns("__pycache__")) if s.is_dir() else shutil.copy(s, t)
        h = hashlib.sha256()
        for f in sorted(x for x in d.rglob("*") if x.is_file() and "__pycache__" not in x.parts):
            h.update(str(f.relative_to(d)).encode())
            h.update(f.read_bytes())
        lock.append(f"architect/{skill}: {{source: image, sha256: {h.hexdigest()}}}")
    (ROOT / "skills.lock.example").write_text(
        "# One entry per skill: source and content hash (sorted relative paths + bytes). Regenerate with build.py.\n"
        + "\n".join(lock) + "\n")
    print(f"built {len(lock)} skills")


if __name__ == "__main__":
    main()
