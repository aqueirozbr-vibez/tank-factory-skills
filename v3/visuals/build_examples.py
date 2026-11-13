#!/usr/bin/env python3
"""Render the sample product's 28 building blocks as boards, one high-resolution PNG each.

Every board is built from the files in examples/reading-capture, so the pictures and the
sample files cannot drift apart: change a file, run this again.

Usage (from the pack root):
    python3 visuals/build_examples.py --fonts <node_modules> [--out visuals/examples]

Needs: the Python packages `markdown` and `playwright` (with Chromium), the Mermaid CLI
`mmdc`, and the npm packages @fontsource-variable/instrument-sans,
@fontsource-variable/geist-mono and @fontsource/vt323 installed under <node_modules>.

© 2026 Tank Factory · CC BY 4.0
"""
import argparse
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import markdown
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from blocks import BLOCKS, ESSENTIALS, LINKS, LINTS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = ROOT / "examples" / "reading-capture"
CREDIT = "© 2026 Tank Factory · CC BY 4.0"
WORK = pathlib.Path(tempfile.mkdtemp(prefix="tf-boards-"))

INK, MUTED, CARBON, PAPER, GROUND = "#171c21", "#55606c", "#526675", "#f7f9fb", "#eceff2"


# ── reading the sample files ─────────────────────────────────────────────

def section(text, heading):
    """Return one heading's section, its sub-headings included."""
    lines, fence = text.splitlines(), False
    for i, line in enumerate(lines):
        m = re.match(r"^(#{2,4}) (.*)$", line)
        if m and m.group(2).strip() == heading:
            level, out = len(m.group(1)), [line]
            for nxt in lines[i + 1:]:
                if nxt.startswith("```"):
                    fence = not fence
                m2 = None if fence else re.match(r"^(#{1,4}) ", nxt)
                if m2 and len(m2.group(1)) <= level:
                    break
                out.append(nxt)
            return "\n".join(out).rstrip()
    raise KeyError(f"{heading} not found")


def md_sections3(md_text):
    """(title, body) for each ### heading."""
    parts = re.split(r"^### (.+)$", md_text, flags=re.M)
    return list(zip(parts[1::2], parts[2::2]))


def singular(noun):
    """'rows' -> 'row', 'entities' -> 'entity', 'objects traced' -> 'object traced'."""
    head, _, tail = noun.partition(" ")
    if not noun.endswith("s") and head.endswith("s"):
        return (head[:-3] + "y" if head.endswith("ies") else head[:-1]) + " " + tail
    word = noun.split(" ")[-1]
    one = word[:-3] + "y" if word.endswith("ies") else word[:-1] if word.endswith("s") else word
    return noun[: len(noun) - len(word)] + one


def first_table_rows(md_text):
    rows, seen = [], False
    for line in md_text.splitlines():
        if line.startswith("|"):
            seen = True
            if not set(line) <= set("|-: "):
                rows.append(line)
        elif seen and rows:
            break
    return rows[1:]


def lint_results():
    out = {}
    for key, (skill, script, args) in LINTS.items():
        cmd = [sys.executable, str(ROOT / "architect" / skill / "scripts" / script)] + args
        p = subprocess.run(cmd, cwd=EX, capture_output=True, text=True)
        m = re.search(r"(\d+) fail, (\d+) warn", p.stdout)
        out[key] = (skill, script, int(m.group(1)) if m else -1, int(m.group(2)) if m else -1)
    return out


# ── diagrams and screenshots ─────────────────────────────────────────────

def render_mermaid(code):
    h = hashlib.sha1(code.encode()).hexdigest()[:12]
    src, png = WORK / f"m-{h}.mmd", WORK / f"m-{h}.png"
    if not png.exists():
        src.write_text(code)
        cfg = WORK / "mermaid.json"
        cfg.write_text(json.dumps({"theme": "base", "themeVariables": {
            "fontFamily": "Arial, sans-serif", "primaryColor": "#f7f9fb", "primaryBorderColor": "#171c21",
            "primaryTextColor": "#171c21", "secondaryColor": "#e4ecf3", "tertiaryColor": "#eceff2",
            "lineColor": "#526675", "textColor": "#171c21", "noteBkgColor": "#e4ecf3", "noteBorderColor": "#526675",
            "actorBkg": "#f7f9fb", "actorBorder": "#171c21", "signalColor": "#526675", "labelBoxBkgColor": "#e4ecf3",
            "edgeLabelBackground": "#ffffff", "clusterBkg": "#eceff2", "clusterBorder": "#526675"}}))
        subprocess.run(["mmdc", "-i", src, "-o", png, "-s", "2", "-b", "white", "-w", "1100",
                        "-c", cfg], check=True, capture_output=True)
    return png


def shoot_wireframes(page):
    """Screens at 1280, 768 and 360 px, and the drawn states, for every wireframe."""
    shots = {}
    for wf in sorted((EX / "docs/design/wireframes").glob("*.html")):
        sid = wf.stem.split("-")[0].upper() + "-" + wf.stem.split("-")[1]
        for w in (1280, 768, 360):
            page.set_viewport_size({"width": w, "height": 900})
            page.goto(wf.as_uri())
            out = WORK / f"{wf.stem}-{w}.png"
            page.locator("main").screenshot(path=str(out))
            shots[(sid, w)] = out
        page.set_viewport_size({"width": 1280, "height": 900})
        page.goto(wf.as_uri())
        out = WORK / f"{wf.stem}-states.png"
        page.locator("section.states").screenshot(path=str(out))
        shots[(sid, "states")] = out
    return shots


def md_to_html(md_text):
    diagrams = []

    def keep(m):
        diagrams.append(m.group(1))
        return f"\n\nMERMAID{len(diagrams) - 1}HOLD\n\n"

    md_text = re.sub(r"```mermaid\n(.*?)```", keep, md_text, flags=re.S)
    md_text = re.sub(r"```json stack_profile", "```json", md_text)
    out = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    out = re.sub(r"(?<![\"'=])(https?://[^\s<]+)", r'<span class="url">\1</span>', out)
    out = re.sub(r"<td>(.*?)</td>", lambda m: "<td>" + re.sub(r"<code>(.*?)</code>", lambda c: "<code>" + re.sub(r"([/_.,])", r"\1<wbr>", c.group(1)) + "</code>", m.group(1)) + "</td>", out, flags=re.S)
    for i, code in enumerate(diagrams):
        png = render_mermaid(code)
        out = out.replace(f"<p>MERMAID{i}HOLD</p>", (
            '<div class="lab"><span>The text in the file</span><span>```mermaid</span></div>'
            f"<pre>{html.escape(code.rstrip())}</pre>"
            '<div class="lab"><span>What it draws · a preview, not part of the file</span></div>'
            f'<div class="prev"><img src="{png.as_uri()}" alt="Rendered diagram"></div>'))
    return out


# ── board markup ─────────────────────────────────────────────────────────

def head(fonts):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
@font-face{{font-family:'Instrument Sans';src:url('{fonts}/@fontsource-variable/instrument-sans/files/instrument-sans-latin-wght-normal.woff2') format('woff2');font-weight:400 700}}
@font-face{{font-family:'Geist Mono';src:url('{fonts}/@fontsource-variable/geist-mono/files/geist-mono-latin-wght-normal.woff2') format('woff2');font-weight:400 600}}
@font-face{{font-family:'VT323';src:url('{fonts}/@fontsource/vt323/files/vt323-latin-400-normal.woff2') format('woff2')}}
*{{box-sizing:border-box}} body{{margin:0;background:{GROUND}}}
h1,h2,h3,h4,p,ul,ol,pre{{margin:0}}
.board{{width:1600px;background:{GROUND};font-family:'Instrument Sans',Arial,sans-serif;color:{INK};padding:64px;display:flex;flex-direction:column;gap:40px}}
.mono{{font-family:'Geist Mono',ui-monospace,monospace}}
.eyebrow{{font:500 13px/16px 'Geist Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:{MUTED}}}
.win{{flex:1;min-width:0;background:{PAPER};border:1px solid {INK};box-shadow:4px 4px 0 0 {INK};display:flex;flex-direction:column}}
.bar{{display:flex;justify-content:space-between;align-items:center;background:{INK};padding:6px 16px;font:400 20px/20px 'VT323',monospace;color:#fff;text-transform:uppercase}}
.doc{{padding:32px 36px 36px;display:flex;flex-direction:column;gap:18px;font-size:15px;line-height:22px}}
.doc h2{{font-size:28px;line-height:32px;font-weight:500;letter-spacing:-.02em}}
.doc h2::before{{content:'##';font:400 15px 'Geist Mono',monospace;color:{MUTED};margin-right:10px}}
.doc h3{{font-size:21px;line-height:26px;font-weight:500;letter-spacing:-.015em;margin-top:6px}}
.doc h3::before{{content:'###';font:400 14px 'Geist Mono',monospace;color:{MUTED};margin-right:10px}}
.doc h4::before{{content:'####';font:400 13px 'Geist Mono',monospace;color:{MUTED};margin-right:10px}}
.doc ul,.doc ol{{padding-left:20px;display:flex;flex-direction:column;gap:4px}}
.doc table{{border-collapse:collapse;width:100%}}
.doc th{{font:500 11px/16px 'Geist Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:{MUTED};text-align:left;padding:0 10px 8px 0;border-bottom:1px solid {INK};vertical-align:bottom}}
.doc td{{font-size:13.5px;line-height:19px;padding:9px 10px 9px 0;border-bottom:1px solid #171c2159;vertical-align:top}}
.url{{overflow-wrap:anywhere}}
.doc code{{font-family:'Geist Mono',monospace;font-size:12px;line-height:18px;background:#e4ecf3;padding:0 3px}}
.doc pre{{font:400 12px/18px 'Geist Mono',monospace;background:#fff;border:1px solid #171c2159;padding:14px 18px;white-space:pre-wrap;overflow-wrap:anywhere}}
.doc pre code{{background:none;padding:0}}
.lab{{display:flex;justify-content:space-between;font:500 11px/16px 'Geist Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:{MUTED}}}
.prev{{background:#fff;border:1px solid #171c2159;padding:12px;display:flex;justify-content:center}}
.prev img{{max-width:100%;max-height:900px;width:auto;display:block}}
.shot{{background:#fff;border:1px solid #171c2159;padding:12px;display:flex;flex-direction:column;gap:8px}}
.shot img{{max-width:100%;display:block;border:1px solid #171c2159}}
.rail{{width:440px;flex:none;display:flex;flex-direction:column;gap:20px}}
.card{{background:{CARBON};color:#eef1f4;padding:24px;display:flex;flex-direction:column;gap:10px;font-size:15px;line-height:22px}}
.card .eyebrow{{color:#dde5ec;font-size:11px}}
.card code{{font-family:'Geist Mono',monospace;font-size:13px}}
.ok{{align-self:flex-start;font:500 12px/20px 'Geist Mono',monospace;color:#346b4a;background:#e3f0e8;border:1px solid #346b4a;padding:0 8px}}
.bad{{align-self:flex-start;font:500 12px/20px 'Geist Mono',monospace;color:#a63d35;background:#f6e3e0;border:1px solid #a63d35;padding:0 8px}}
.white{{background:#fff;border:1px solid {INK};padding:20px;display:flex;flex-direction:column;gap:10px;font-size:14px;line-height:20px}}
.white .eyebrow{{font-size:11px}}
.pair{{display:flex;gap:10px;align-items:flex-start}} .pair span{{flex:none}}
.pair code{{font-family:'Geist Mono',monospace;font-size:12px}}
.foot{{display:flex;justify-content:space-between;font:500 12px/16px 'Geist Mono',monospace;letter-spacing:.06em;color:{MUTED};border-top:1px solid #171c2159;padding-top:16px}}
.swatches{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.sw{{background:#fff;border:1px solid #171c2159;display:flex;flex-direction:column}}
.sw i{{height:56px;border-bottom:1px solid #171c2159}}
.sw p{{padding:6px 10px;font:500 12px/16px 'Geist Mono',monospace}}
.sw p+p{{padding-top:0;color:{MUTED};font-weight:400}}
</style></head><body>"""


def header(b):
    ess_name, ess_file, names = ESSENTIALS[b["ess"]]
    cells = "".join(
        f'<p style="font-size:13px;line-height:18px;padding:5px 12px;{"background:%s;color:#fff" % INK if i + 1 == b["n"] else "color:%s" % MUTED}">{i + 1} · {html.escape(n)}</p>'
        for i, n in enumerate(names))
    cols = 2 if len(names) > 4 else 1
    return f"""<div style="display:flex;gap:40px;align-items:flex-end">
<div style="flex:1;display:flex;flex-direction:column;gap:12px">
<p class="eyebrow">{ess_name} · block {b['n']} of {len(names)} · {b['id']}</p>
<h1 style="font-size:56px;line-height:60px;font-weight:500;letter-spacing:-.035em">{html.escape(b['title'])}</h1>
<p style="font-size:20px;line-height:28px;color:{MUTED};max-width:900px">{html.escape(b['desc'])}</p></div>
<div style="width:440px;flex:none;display:grid;grid-template-columns:repeat({cols},minmax(0,1fr));grid-auto-flow:column;grid-template-rows:auto repeat({-(-len(names) // cols)},auto);border:1px solid {INK};background:#fff">
<p class="eyebrow" style="grid-column:1 / -1;font-size:11px;padding:8px 12px;border-bottom:1px solid {INK}">{html.escape(b['file'])}</p>{cells}</div></div>"""


def rail(b, lints, badges):
    skill, script, fails, warns = lints[b["lint"]]
    must = "".join(f"<p>✓ {html.escape(m)}</p>" for m in b["must"])
    feeds = "".join(f"<p>→ {f}</p>" for f in b["feeds"])
    result = (f'<p class="ok">✓ {script} · {fails} fail · {warns} warn</p>' if fails == 0
              else f'<p class="bad">× {script} · {fails} fail</p>')
    badges_html = "".join(f'<p class="ok">✓ {html.escape(x)}</p>' for x in badges)
    return f"""<div class="rail">
<div class="card"><p class="eyebrow">Must contain</p>{must}</div>
<div class="card"><p class="eyebrow">Done when</p><p>{html.escape(b['done'])}</p>{badges_html}</div>
<div class="card"><p class="eyebrow">Feeds</p>{feeds}</div>
<div class="white"><p class="eyebrow">Written and checked by</p>
<p>The <b class="mono" style="font-size:13px">{skill}</b> skill writes this block; its check script runs the same test as the stage gate.</p>
<p class="mono" style="font-size:12px;color:{MUTED}">v3/architect/{skill}/scripts/{script}</p>{result}</div>
<div class="white"><p class="eyebrow">Rewrite to pass the gate</p>
<div class="pair"><span class="bad">× weak</span><p>{html.escape(b['weak'])}</p></div>
<div class="pair"><span class="ok">✓ strong</span><p>{b['strong']}</p></div></div>
</div>"""


def foot(name):
    return f'<div class="foot"><span>{CREDIT}</span><span>Tank Factory v3 · Architect skill pack · {name}</span></div>'


def board_block(b, lints, shots):
    text = (EX / b["file"]).read_text()
    body_md = "\n\n".join(section(text, s) for s in b["sections"])
    badges = []
    if b.get("count"):
        sec, noun, sourced = b["count"]
        rows = first_table_rows(section(text, sec))
        badges.append(f"{len(rows)} {noun if len(rows) != 1 else singular(noun)} in the table")
        if sourced:
            ok = sum(1 for r in rows if "http" in r or "`" in r)
            badges.append(f"{ok} of {len(rows)} rows carry a source")
    special = b.get("special")
    extra = ""
    if special == "swatches":
        toks = [r.strip("|").split("|") for r in first_table_rows(section(text, "Tokens"))]
        sw = "".join(f'<div class="sw"><i style="background:{c[2].strip()}"></i><p>{c[0].strip()}</p><p>{c[2].strip()}</p></div>'
                     for c in toks if c[1].strip() == "colour")
        extra = f'<div class="lab"><span>Colour tokens · a preview, not part of the file</span></div><div class="swatches">{sw}</div>'
    if special == "curve":
        for title, body in md_sections3(section(text, "Journey maps")):
            rows = [r.strip("|").split("|") for r in first_table_rows(body)]
            pts = []
            for r in rows:
                m = re.match(r"\s*([+\-−]?\d)", r[5])
                if m:
                    pts.append((r[0].strip(), r[1].strip(), int(m.group(1).replace("−", "-"))))
            W, H, pad = 860, 220, 40
            step = (W - 2 * pad) / max(1, len(pts) - 1)
            y = lambda v: H / 2 - v * (H / 2 - 30) / 2
            xy = [(pad + i * step, y(v)) for i, (_, _, v) in enumerate(pts)]
            grid = "".join(f'<line x1="{pad}" x2="{W - pad}" y1="{y(v)}" y2="{y(v)}" stroke="#171c21" stroke-opacity="{.5 if v == 0 else .12}"/>'
                           f'<text x="4" y="{y(v) + 4}" font-size="11" fill="{MUTED}" font-family="Geist Mono">{v:+d}</text>' for v in (-2, -1, 0, 1, 2))
            line = " ".join(f"{x:.0f},{yy:.0f}" for x, yy in xy)
            dots = "".join(f'<circle cx="{x:.0f}" cy="{yy:.0f}" r="6" fill="{"#a63d35" if v < 0 else CARBON}"/>'
                           f'<text x="{x:.0f}" y="{H - 6}" text-anchor="middle" font-size="12" fill="{INK}" font-family="Geist Mono">{html.escape(s)}</text>'
                           for (x, yy), (s, _, v) in zip(xy, pts))
            extra += (f'<div class="lab"><span>{html.escape(title)} · emotion curve · a preview, not part of the file</span></div>'
                      f'<div class="prev"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Emotion curve">{grid}'
                      f'<polyline points="{line}" fill="none" stroke="{CARBON}" stroke-width="3"/>{dots}</svg></div>')
    if special == "desktop":
        imgs = "".join(f'<div class="shot"><p class="lab"><span>{sid} · 1280 px · docs/design/wireframes/</span></p><img src="{p.as_uri()}"></div>'
                       for (sid, w), p in sorted(shots.items(), key=lambda kv: str(kv[0])) if w == 1280)
        extra = f'<div class="lab"><span>The wireframes these prompts produced</span></div>{imgs}'
    if special == "mobile":
        ui = (EX / UI_PATH).read_text()
        lines = [l for l in ui.splitlines() if l.startswith("- Mobile view:")]
        sids = [h for h in re.findall(r"^### (S-\d+ — .+)$", ui, re.M)]
        mob = "".join(f"<li><b>{html.escape(s)}</b> — {html.escape(l[len('- Mobile view:'):].strip())}</li>" for s, l in zip(sids, lines))
        body_md = section((EX / "docs/design/styleguide.md").read_text(), "Breakpoints")
        extra = f'<h3>Mobile view, per screen prompt</h3><ul>{mob}</ul>'
        for sid in sorted({k[0] for k in shots}):
            extra += (f'<div class="shot"><p class="lab"><span>{sid} · 360 px and 768 px · one wireframe file, its @media rules</span></p>'
                      f'<div style="display:flex;gap:16px;align-items:flex-start"><img style="width:300px" src="{shots[(sid, 360)].as_uri()}">'
                      f'<img style="width:560px" src="{shots[(sid, 768)].as_uri()}"></div></div>')
    if special == "states":
        for sid in sorted({k[0] for k in shots}):
            extra += f'<div class="shot"><p class="lab"><span>{sid} · the states drawn in its wireframe</span></p><img src="{shots[(sid, "states")].as_uri()}"></div>'
    if b.get("extra_file"):
        src = (EX / b["extra_file"]).read_text()
        extra += (f'<div class="lab"><span>And in {html.escape(b["extra_file"])}</span></div><pre>{html.escape(src.rstrip())}</pre>')
    sec_label = " · ".join(b["sections"]) if special != "mobile" else "Breakpoints · Mobile view"
    return f"""<div class="board">{header(b)}
<div style="display:flex;gap:40px;align-items:stretch">
<div class="win"><div class="bar"><span>{html.escape(b['file'])}</span><span>§ {html.escape(sec_label)}</span></div>
<div class="doc">{md_to_html(body_md)}{extra}</div></div>
{rail(b, lints, badges)}</div>{foot(b['id'] + ' ' + b['title'])}</div>"""


UI_PATH = "docs/design/ui-prompts.md"


def board_overview(lints):
    cards = ""
    for i, (name, path, names) in enumerate(ESSENTIALS):
        ids = [b["id"] for b in BLOCKS if b["ess"] == i]
        items = "".join(f"<li>{bid} {html.escape(n)}</li>" for bid, n in zip(ids, names))
        cards += f"""<div class="win"><div class="bar"><span>{name}</span><span>{len(names)} blocks</span></div>
<div class="doc" style="padding:20px 24px;gap:12px"><code style="background:none;padding:0">{html.escape(path)}</code><ul>{items}</ul></div></div>"""
    checks = "".join(f'<p class="ok">✓ {s} · {f} fail</p>' for (_, s, f, _w) in lints.values())
    return f"""<div class="board" style="background:radial-gradient(ellipse at 50% 0%, #e4ecf3 0%, {GROUND} 60%)">
<div style="display:flex;flex-direction:column;gap:16px;align-items:center;text-align:center">
<p class="eyebrow">Tank Factory · The Initial Context · worked example</p>
<h1 style="font-size:72px;line-height:72px;font-weight:500;letter-spacing:-.04em;max-width:1200px">Reading Capture, Written Through All Four Essentials</h1>
<p style="font-size:20px;line-height:28px;color:{MUTED};max-width:960px">The skill pack’s sample product, one board per building block. Every board is rendered from the files in <span class="mono" style="font-size:17px">v3/examples/reading-capture</span>, and every file passes its skill’s check script.</p></div>
<div style="display:flex;gap:32px;align-items:stretch">
<div class="win"><div class="bar"><span>The product</span><span>fictional</span></div>
<div class="doc" style="padding:24px 28px"><p style="font-size:17px;line-height:26px">Reading Capture lets a <b>Field Inspector</b> record meter readings on a phone, with or without signal, and sends readings outside their range to the <b>Maintenance Planner</b> the same day. Assets come from the <b>Asset Registry</b>, which is only ever read; a model writes one sentence per anomaly and decides nothing.</p>
<p style="font-size:14px;line-height:20px;color:{MUTED}">The product, people, numbers and links are invented for teaching.</p></div></div>
<div class="card" style="width:520px;flex:none"><p class="eyebrow">Every check script, run on these files</p>{checks}</div></div>
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:32px;align-items:start">{cards}</div>
<div class="white"><p class="eyebrow">How to read every board</p>
<p>The window holds the sample file, as the factory reads it; diagrams show their Mermaid text and a preview. The carbon rail is the lesson: what the block must contain, the test that says it is done, what it feeds, the skill and check script behind it, and a weak line rewritten into one that passes.</p></div>
{foot('Overview')}</div>"""


def board_links():
    rows = "".join(f"""<div style="display:flex;gap:20px;align-items:flex-start;padding:14px 0;border-top:1px solid #171c2159">
<span class="ok" style="flex:none">✓</span><div style="flex:1;display:flex;flex-direction:column;gap:4px">
<p style="font-size:20px;line-height:26px">{html.escape(t)}</p><p class="eyebrow" style="font-size:12px">{html.escape(e)}</p></div>
<p class="mono" style="width:520px;flex:none;font-size:13px;line-height:20px;color:{MUTED}">{html.escape(c)}</p></div>"""
                   for t, e, c in LINKS)
    return f"""<div class="board"><div style="display:flex;flex-direction:column;gap:12px">
<p class="eyebrow">Before the context build · handover check</p>
<h1 style="font-size:56px;line-height:60px;font-weight:500;letter-spacing:-.035em">Fourteen Links That Must Hold</h1>
<p style="font-size:20px;line-height:28px;color:{MUTED};max-width:1100px">Each link joins two blocks. In the pack, a check script proves it, so the handover check is something you run, not something you read.</p></div>
<div class="win"><div class="bar"><span>Reading Capture</span><span>{len(LINKS)} of {len(LINKS)} hold</span></div><div class="doc">{rows}</div></div>
{foot('Fourteen links')}</div>"""


# ── main ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True, type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "visuals" / "examples")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    lints = lint_results()
    bad = {k: v for k, v in lints.items() if v[2] != 0}
    if bad:
        sys.exit(f"check scripts fail on the sample product: {bad}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        shots = shoot_wireframes(page)
        boards = [("00-overview", board_overview(lints))]
        boards += [(f"{i:02d}-{b['id']}-{re.sub(r'[^a-z0-9]+', '-', b['title'].lower()).strip('-')}", board_block(b, lints, shots))
                   for i, b in enumerate(BLOCKS, 1)]
        boards.append((f"{len(BLOCKS) + 1:02d}-handover-links", board_links()))
        page.set_viewport_size({"width": 1600, "height": 1000})
        for name, body in boards:
            f = WORK / f"{name}.html"
            f.write_text(head(a.fonts.resolve()) + body + "</body></html>")
            page.goto(f.as_uri())
            page.evaluate("async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => null))); }")
            page.locator(".board").screenshot(path=str(a.out / f"{name}.png"))
            try:
                import oxipng  # optional: lossless compression
                oxipng.optimize(a.out / f"{name}.png", level=3)
            except ImportError:
                pass
            print(name)
        browser.close()


if __name__ == "__main__":
    main()
