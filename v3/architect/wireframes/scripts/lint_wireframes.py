#!/usr/bin/env python3
# © 2026 Tank Factory · CC BY 4.0
"""Wireframe gate for docs/design/wireframes/*.html.

Usage: python3 lint_wireframes.py docs/design/wireframes --prd docs/prd/<product>.md
           [--styleguide docs/design/styleguide.md] [--ui-prompts docs/design/ui-prompts.md]

Checks the branding gate for the wireframe path: one wireframe per PRD screen
id, valid HTML, no external network references, tokens as CSS variables — and
the mobile view and component states the UI brief asks for. Exit 1 on any FAIL.
"""
import argparse
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _md as md  # noqa: E402

SCREEN = r"[A-Z]{1,3}-\d{2,3}"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.tags, self.states = [], [], [], set()
        self.attrs_all, self.body_screen, self.text = [], None, []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append(tag)
        self.attrs_all.append((tag, d))
        if tag == "body":
            self.body_screen = d.get("data-screen")
        if d.get("data-component") and d.get("data-state"):
            self.states.add((d["data-component"], d["data-state"].lower()))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.attrs_all.append((tag, dict(attrs)))
        self.tags.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            if tag in self.stack:  # implicit closes (p, li, td…) are tolerated
                while self.stack and self.stack[-1] != tag:
                    inner = self.stack.pop()
                    if inner not in {"p", "li", "td", "th", "tr", "option", "dt", "dd", "tbody", "thead"}:
                        self.errors.append(f"<{inner}> not closed before </{tag}>")
                self.stack.pop()
            else:
                self.errors.append(f"</{tag}> with no matching <{tag}>")
        else:
            self.stack.pop()

    def handle_data(self, data):
        self.text.append(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--prd", required=True)
    ap.add_argument("--styleguide")
    ap.add_argument("--ui-prompts")
    a = ap.parse_args()
    rep = md.Report("wireframe gate")

    prd = md.read(a.prd)
    hdr, rows = md.table(md.section(prd, "Journeys and screens") or "", ["Screen", "Name", "Purpose"])
    screens = [r[0].strip("*` ") for r in rows]
    if not screens:
        rep.fail("the PRD names no screens; there is nothing to draw")

    tokens, messages = [], {}
    if a.styleguide:
        sg = md.read(a.styleguide)
        th, trows = md.table(md.section(sg, "Tokens") or "", ["Token", "Category", "Value"])
        tokens = ["--" + r[0].strip("*` ").replace(".", "-") for r in trows]
        sh, srows = md.table(md.section(sg, "Component states") or "", ["Component", "State", "Appearance", "Message"])
        for r in srows:
            m = md.cell(r, sh, "Message")
            if not md.is_empty(m):
                messages[(r[0].strip("*` "), md.cell(r, sh, "State").strip("*` ").lower())] = m.strip()

    wanted = {}
    if a.ui_prompts:
        for t, b in md.sections(md.section(md.read(a.ui_prompts), "Screen prompts") or "", 3):
            m = re.match(r"^(" + SCREEN + r")\b", t)
            if not m:
                continue
            for part in [x for x in (md.labelled(b, "States") or "").split(";") if ":" in x]:
                c, lst = part.split(":", 1)
                for s in [x.strip("*` .").lower() for x in lst.split(",") if x.strip()]:
                    wanted.setdefault(m.group(1), set()).add((c.strip("*` "), s))

    files = sorted(f for f in os.listdir(a.dir) if f.endswith(".html")) if os.path.isdir(a.dir) else []
    by_screen = {}
    for f in files:
        m = re.match(r"^(" + SCREEN + r")\b", f.upper())
        if not m:
            rep.fail(f"{f}: file name must start with a screen id (s-01-name.html)")
            continue
        by_screen.setdefault(m.group(1), []).append(f)
    for sid in screens:
        n = len(by_screen.get(sid, []))
        if n != 1:
            rep.fail(f"screen {sid}: {n} wireframes; need exactly 1")
    for sid in sorted(set(by_screen) - set(screens)):
        rep.fail(f"{by_screen[sid][0]}: {sid} is not in the PRD's screens map")

    for sid, fs in sorted(by_screen.items()):
        f = fs[0]
        raw = md.read(os.path.join(a.dir, f))
        if not raw.lstrip().lower().startswith("<!doctype html"):
            rep.fail(f"{f}: must start with <!doctype html>")
        page = Page()
        try:
            page.feed(raw)
            page.close()
        except Exception as exc:  # noqa: BLE001
            rep.fail(f"{f}: does not parse as HTML: {exc}")
            continue
        for e in page.errors[:5]:
            rep.fail(f"{f}: invalid HTML: {e}")
        for left in [t for t in page.stack if t not in {"p", "li", "td", "th", "tr", "tbody", "thead"}]:
            rep.fail(f"{f}: <{left}> never closed")
        for need in ("html", "head", "title", "body", "main", "h1", "style"):
            if need not in page.tags:
                rep.fail(f"{f}: no <{need}> element")
        if not any(t == "meta" and d.get("name") == "viewport" for t, d in page.attrs_all):
            rep.fail(f"{f}: no <meta name=\"viewport\">, so the mobile view cannot render")
        if page.body_screen != sid:
            rep.fail(f"{f}: <body data-screen> is '{page.body_screen}', expected '{sid}'")
        if "script" in page.tags:
            rep.fail(f"{f}: <script> found; a wireframe is static")

        for m in re.finditer(r"""(?:src|href|action|poster|data)\s*=\s*["']?\s*((?:https?:)?//[^"'\s>]+)""", raw, re.I):
            rep.fail(f"{f}: external reference {m.group(1)[:60]}")
        for m in re.finditer(r"""url\(\s*["']?\s*((?:https?:)?//[^)"'\s]+)""", raw, re.I):
            rep.fail(f"{f}: external url() {m.group(1)[:60]}")
        if re.search(r"@import", raw, re.I):
            rep.fail(f"{f}: @import found; keep all CSS in the one <style> block")
        if any(t == "link" and "stylesheet" in (d.get("rel") or "") for t, d in page.attrs_all):
            rep.fail(f"{f}: <link rel=stylesheet> found; keep all CSS in the one <style> block")

        css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", raw, re.S | re.I))
        root = re.search(r":root\s*\{(.*?)\}", css, re.S)
        declared = set(re.findall(r"(--[a-z0-9-]+)\s*:", root.group(1))) if root else set()
        if not declared:
            rep.fail(f"{f}: no CSS variables declared in :root")
        for v in sorted(set(re.findall(r"var\(\s*(--[a-z0-9-]+)", raw)) - declared):
            rep.fail(f"{f}: var({v}) is used but not declared in :root")
        for t in tokens:
            if t not in declared:
                rep.fail(f"{f}: styleguide token {t} is not declared in :root")
        if tokens:
            body_css = css.replace(root.group(0), "") if root else css
            for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", body_css):
                rep.warn(f"{f}: raw colour {m.group(0)} outside :root; use a token variable")
                break
        if "@media" not in css:
            rep.fail(f"{f}: no @media rule, so there is no mobile and desktop layout")
        if re.search(r"lorem ipsum", raw, re.I):
            rep.fail(f"{f}: filler text; use the PRD's example values")

        text = re.sub(r"\s+", " ", " ".join(page.text))
        for (c, s) in sorted(wanted.get(sid, set())):
            if (c, s) not in page.states:
                rep.fail(f"{f}: state '{c}: {s}' from the screen prompt is not drawn (data-component / data-state)")
            elif (c, s) in messages and messages[(c, s)] not in text:
                rep.fail(f"{f}: state '{c}: {s}' does not show the styleguide message \"{messages[(c, s)][:50]}\"")
        if not a.ui_prompts and not page.states:
            rep.warn(f"{f}: no component states drawn")

    rep.finish()


if __name__ == "__main__":
    main()
