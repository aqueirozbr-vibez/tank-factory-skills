#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""stack_profile gate.

Usage: python3 lint_stack_profile.py <docs/trd/<product>.md | profile.json | ->
           --guardrails <environment.yaml> [--prd docs/prd/<product>.md]
           [--supported supported-stacks.json] [--new-product] [--repo <path>]

Reads the profile from the TRD's ```json stack_profile block, a JSON file, or
stdin (-). Checks: every field present for every repository; each stack is a
supported stack; every base image from an allowed source; every registry and
destination inside the guardrails or listed in guardrail_requests[];
product_kind agrees with the PRD's screens; a template for every repository
of a new product; with --repo, versions match the manifests. Exit 1 on FAIL.
"""
import argparse
import fnmatch
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

FIELDS = ["repository", "languages", "package_manager", "base_image", "quality",
          "boundary_check", "bindings", "scanners", "load_test"]
QUALITY = ["format", "lint", "typecheck", "test", "focused_test_pattern"]
KINDS = {"ui", "service", "ui_and_service"}
REQ_KINDS = {"registry", "base_image_source", "network"}


def simple_yaml(path):
    """Top-level `key: [a, b]` and `key:` + `- item` lists; enough for environment.yaml."""
    out, key = {}, None
    for raw in md.read(path).splitlines():
        ln = raw.split(" #")[0].rstrip()
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("["):
                out[key] = [x.strip().strip("'\"") for x in val.strip("[]").split(",") if x.strip()]
            else:
                out[key] = [val.strip("'\"")] if val else []
        elif key and re.match(r"^\s*-\s+", ln):
            out[key].append(re.sub(r"^\s*-\s+", "", ln).strip().strip("'\""))
    return out


def load_profile(src, rep):
    raw = sys.stdin.read() if src == "-" else md.read(src)
    if src.endswith(".md"):
        m = re.search(r"```json\s+stack_profile\s*\n(.*?)\n```", raw, re.S)
        if not m:
            rep.fail("no ```json stack_profile block in the TRD's Stack section")
            return None
        raw = m.group(1)
    try:
        return json.loads(raw)
    except ValueError as exc:
        rep.fail(f"profile is not valid JSON: {exc}")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--guardrails", required=True)
    ap.add_argument("--prd")
    ap.add_argument("--supported", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         "..", "references", "supported-stacks.json"))
    ap.add_argument("--new-product", action="store_true")
    ap.add_argument("--repo", help="checkout root, to compare versions with manifests (as-built)")
    a = ap.parse_args()
    rep = md.Report("stack_profile gate")
    prof = load_profile(a.source, rep)
    if prof is None:
        rep.finish()
    guard = simple_yaml(a.guardrails)
    stacks = json.loads(md.read(a.supported))["stacks"]
    by_lang = {l: s for s in stacks for l in s["languages"]}

    kind = prof.get("product_kind")
    if kind not in KINDS:
        rep.fail(f"product_kind '{kind}' must be ui, service or ui_and_service")
    if a.prd:
        prd = md.read(a.prd)
        prd_kind = (md.labelled(md.section(prd, "Summary") or "", "Product kind") or "").strip("`* ").lower()
        has_screens = bool(re.search(r"^\s*Screens\s*:\s*\S", prd, re.M))
        if prd_kind and kind != prd_kind:
            rep.fail(f"product_kind '{kind}' disagrees with the PRD's 'Product kind: {prd_kind}'")
        if has_screens and kind == "service":
            rep.fail("product_kind is service but the PRD names screens")
        if not has_screens and kind in {"ui", "ui_and_service"}:
            rep.fail(f"product_kind is {kind} but the PRD names no screens")

    requests = prof.get("guardrail_requests", [])
    if not isinstance(requests, list):
        rep.fail("guardrail_requests must be a list (empty when nothing is needed)")
        requests = []
    for r in requests:
        if r.get("kind") not in REQ_KINDS:
            rep.fail(f"guardrail request kind '{r.get('kind')}' must be registry, base_image_source or network")
        if not r.get("value") or not r.get("reason"):
            rep.fail(f"guardrail request {r} needs a value and a reason")
    asked = {(r.get("kind"), r.get("value")) for r in requests}

    repos = prof.get("repositories") or []
    if not repos:
        rep.fail("repositories is empty")
    names = [r.get("repository") for r in repos]
    if len(set(names)) != len(names):
        rep.fail("a repository is listed twice")

    for r in repos:
        name = r.get("repository", "?")
        for f in FIELDS:
            if not r.get(f):
                rep.fail(f"{name}: field '{f}' missing or empty")
        if not re.match(r"^[\w.-]+/[\w.-]+$", str(r.get("repository", ""))):
            rep.fail(f"{name}: repository must be owner/name")
        q = r.get("quality") or {}
        for f in QUALITY:
            if not q.get(f):
                rep.fail(f"{name}: quality.{f} missing or empty")
        if q.get("focused_test_pattern") and "{files}" not in q["focused_test_pattern"]:
            rep.fail(f"{name}: quality.focused_test_pattern must contain {{files}}")
        if q.get("format") and not re.search(r"check|--diff|verify", q["format"]):
            rep.warn(f"{name}: quality.format '{q['format']}' looks like it rewrites files; use the check-only form")
        cmds = [q.get(k) for k in QUALITY[:4] if q.get(k)]
        if len(set(cmds)) != len(cmds):
            rep.fail(f"{name}: two quality commands are identical")

        stack = None
        for lang in r.get("languages") or []:
            m = re.match(r"^([a-z][\w+#-]*)@(\d[\w.]*)$", str(lang))
            if not m:
                rep.fail(f"{name}: language '{lang}' must be name@version")
                continue
            if m.group(1) not in by_lang:
                rep.fail(f"{name}: '{m.group(1)}' is not a supported stack ({', '.join(sorted(by_lang))})")
            else:
                stack = stack or by_lang[m.group(1)]

        pm = re.match(r"^([a-z][\w-]*)@(\d[\w.]*)$", str(r.get("package_manager", "")))
        if r.get("package_manager") and not pm:
            rep.fail(f"{name}: package_manager '{r['package_manager']}' must be name@version")
        if pm and stack:
            reg = stack["package_managers"].get(pm.group(1))
            if reg is None:
                rep.fail(f"{name}: package manager '{pm.group(1)}' is not part of the {stack['id']} stack")
            elif reg not in guard.get("package_registries", []) and ("registry", reg) not in asked:
                rep.fail(f"{name}: registry {reg} is outside the guardrails and not in guardrail_requests[]")

        img = str(r.get("base_image", ""))
        if img:
            if ":" not in img.split("/")[-1] and "@sha256:" not in img:
                rep.fail(f"{name}: base_image '{img}' has no tag or digest")
            allowed = any(fnmatch.fnmatch(img, pat) or fnmatch.fnmatch(img.split(":")[0], pat.rstrip("*").rstrip("/") + "/*")
                          for pat in guard.get("base_image_sources", []))
            src = img.rsplit("/", 1)[0] if "/" in img else img
            if not allowed and not any(k == "base_image_source" and str(v).rstrip("/*") in src for k, v in asked):
                rep.fail(f"{name}: base image {img} is not from an allowed source and not in guardrail_requests[]")

        if stack:
            for f in ("boundary_check", "bindings", "scanners", "load_test"):
                if r.get(f) and r[f] not in stack[f]:
                    rep.fail(f"{name}: {f} '{r[f]}' is not shipped for the {stack['id']} stack ({', '.join(stack[f])})")
            if r.get("template") and r["template"] not in stack["templates"]:
                rep.fail(f"{name}: template '{r['template']}' is not a {stack['id']} template ({', '.join(stack['templates'])})")
        if a.new_product and not r.get("template"):
            rep.fail(f"{name}: a new product needs a repository template")

        if a.repo:
            root = os.path.join(a.repo, name.split("/")[-1]) if os.path.isdir(os.path.join(a.repo, name.split("/")[-1])) else a.repo
            pj, pp = os.path.join(root, "package.json"), os.path.join(root, "pyproject.toml")
            if pm and os.path.exists(pj):
                declared = json.loads(md.read(pj)).get("packageManager", "")
                if declared and not declared.startswith(f"{pm.group(1)}@{pm.group(2)}"):
                    rep.fail(f"{name}: package_manager {r['package_manager']} but package.json says {declared}")
            if os.path.exists(pp):
                m = re.search(r'requires-python\s*=\s*"[^\d]*(\d+\.\d+)', md.read(pp))
                want = next((l.split("@")[1] for l in r.get("languages", []) if l.startswith("python@")), None)
                if m and want and not want.startswith(m.group(1)):
                    rep.fail(f"{name}: python@{want} but pyproject.toml requires {m.group(1)}")
            locks = {"pnpm": "pnpm-lock.yaml", "npm": "package-lock.json", "yarn": "yarn.lock", "uv": "uv.lock", "poetry": "poetry.lock"}
            if pm and pm.group(1) in locks and os.path.isdir(root) and not os.path.exists(os.path.join(root, locks[pm.group(1)])):
                rep.fail(f"{name}: no {locks[pm.group(1)]} in the repository for {pm.group(1)}")

    for k, v in asked:
        if k == "network" and v in guard.get("network_allowlist", []):
            rep.warn(f"guardrail request for {v} is unnecessary: it is already on the network allowlist")
    rep.finish()


if __name__ == "__main__":
    main()
