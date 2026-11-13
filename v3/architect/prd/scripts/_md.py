# © 2026 Tank Factory · CC BY 4.0
"""Markdown helpers shared by the Architect skills' lint scripts.

Standard library only. Each skill ships its own copy beside its lint script,
so a skill stays self-contained under its `skills.lock` hash.
"""
import re
import sys

PLACEHOLDERS = [r"\bTBD\b", r"\bTODO\b", r"\bTBC\b", r"\bFIXME\b",
                r"to be defined", r"to be decided", r"lorem ipsum"]
VAGUE = [r"\bfast\b(?!-moving)", r"\brobust\b", r"\bscalable\b", r"user-friendly",
         r"\bseamless\b", r"\bintuitive\b"]
EMPTY_CELLS = {"", "-", "—", "–", "n/a", "na", "none", "?", "tbd", "todo", "unknown", "openquestion", "assumed"}


class Report:
    """Collects FAIL and WARN lines, prints them, exits 1 on any FAIL."""

    def __init__(self, name):
        self.name, self.fails, self.warns = name, [], []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def finish(self):
        for w in self.warns:
            print(f"WARN  {w}")
        for f in self.fails:
            print(f"FAIL  {f}")
        print(f"\n{self.name}: {len(self.fails)} fail, {len(self.warns)} warn")
        sys.exit(1 if self.fails else 0)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def strip_code(text):
    """Text with fenced code blocks blanked, line count preserved."""
    out, inside = [], False
    for ln in text.splitlines():
        if ln.strip().startswith("```"):
            inside = not inside
            out.append("")
        else:
            out.append("" if inside else ln)
    return "\n".join(out)


def sections(text, level=2):
    """[(title, body_text)] for headings of `level`; ignores headings inside code fences."""
    res, cur, buf, inside = [], None, [], False
    pat = re.compile(r"^" + "#" * level + r"\s+(.*?)\s*$")
    for ln in text.splitlines():
        if ln.strip().startswith("```"):
            inside = not inside
        m = None if inside else pat.match(ln)
        if m:
            if cur is not None:
                res.append((cur, "\n".join(buf)))
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(ln)
    if cur is not None:
        res.append((cur, "\n".join(buf)))
    return res


def section(text, title, level=2):
    """Body of the first section whose title starts with `title` (case-insensitive), else None."""
    for t, b in sections(text, level):
        if t.lower().startswith(title.lower()):
            return b
    return None


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(text):
    """Yield (header_cells, rows) for every pipe table outside code fences."""
    lines = strip_code(text).splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|\s*:?-{3,}", lines[i + 1]):
            hdr, rows, j = _cells(lines[i]), [], i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(_cells(lines[j]))
                j += 1
            yield hdr, rows
            i = j
        else:
            i += 1


def col(hdr, name):
    """Index of the first header cell containing any `a|b` alternative of `name`, else -1."""
    for alt in name.split("|"):
        for i, h in enumerate(hdr):
            if alt.lower() in h.lower():
                return i
    return -1


def table(text, cols):
    """First table that has every column in `cols`; returns (hdr, rows) or (None, [])."""
    for hdr, rows in tables(text or ""):
        if all(col(hdr, c) >= 0 for c in cols):
            return hdr, rows
    return None, []


def cell(row, hdr, name):
    i = col(hdr, name)
    return row[i] if 0 <= i < len(row) else ""


def is_empty(value, allow=()):
    """True for a blank or filler cell; `allow` lists fillers that are real values here ('none')."""
    v = re.sub(r"[`*_\s]", "", value).lower()
    return v in EMPTY_CELLS and v not in allow


def code_blocks(text, lang=None):
    """Fenced code blocks as (lang, body); `lang` filters by the info string's first word."""
    out, cur, buf = [], None, []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("```"):
            if cur is None:
                cur, buf = (s[3:].strip().split() or [""])[0].lower(), []
            else:
                out.append((cur, "\n".join(buf)))
                cur = None
        elif cur is not None:
            buf.append(ln)
    return [b for b in out if lang is None or b[0] == lang]


def mermaid(text, kind=None):
    """Mermaid blocks; `kind` filters by the diagram keyword on the first non-empty line."""
    res = []
    for _, body in code_blocks(text, "mermaid"):
        first = next((l.strip() for l in body.splitlines() if l.strip()), "")
        if kind is None or first.lower().startswith(kind.lower()):
            res.append(body)
    return res


def bullets(text):
    return [m.group(1).strip() for m in re.finditer(r"^\s*[-*]\s+(.+)$", strip_code(text or ""), re.M)]


def labelled(text, label):
    """Text after `Label:` on its line, else None."""
    m = re.search(r"^\s*(?:[-*]\s+)?\**" + re.escape(label) + r"\**\s*:\s*(.*)$", text or "", re.M | re.I)
    return m.group(1).strip() if m else None


def has_number(s):
    """A real quantity or a named standard; digits inside ids (S-02, FR-1.2) do not count."""
    if re.search(r"WCAG|LGPD|GDPR|ISO|SOC|IEC|NIST|HIPAA|PCI", s):
        return True
    return bool(re.search(r"\d", re.sub(r"\b[A-Z]{1,5}-\d+(?:\.\d+)?\b", "", s)))


def has_source(s):
    """True when the line cites a URL or a repository path (`dir/file.ext`, optional `:line`)."""
    if re.search(r"https?://\S+", s):
        return True
    return bool(re.search(r"`[\w.\-]+(?:/[\w.\-]+)+(?::\d+)?`|`[\w\-]+\.[a-z]{1,5}(?::\d+)?`", s))


def check_placeholders(text, rep, what="document"):
    body = strip_code(text)
    for pat in PLACEHOLDERS:
        for m in re.finditer(pat, body, re.I):
            rep.fail(f"{what} line {body[:m.start()].count(chr(10)) + 1}: placeholder '{m.group(0)}' — write the decision or an open question")
    for m in re.finditer(r"<[A-Z][^<>\n]{2,80}>", body):
        rep.fail(f"{what} line {body[:m.start()].count(chr(10)) + 1}: template placeholder left in: {m.group(0)[:50]}")


def check_vague(text, rep, what="document"):
    body = strip_code(text)
    for pat in VAGUE:
        for m in re.finditer(pat, body, re.I):
            line = body[body.rfind("\n", 0, m.start()) + 1:(body.find("\n", m.end()) + 1 or len(body) + 1) - 1]
            if not has_number(line):  # a number on the same line already says how much
                rep.warn(f"{what} line {body[:m.start()].count(chr(10)) + 1}: '{m.group(0)}' hides a number; state the value")


def ids(text, pattern):
    """Sorted unique matches of an ID pattern such as r'FR-\\d+\\.\\d+'."""
    return sorted(set(re.findall(pattern, text or "")), key=lambda s: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)])


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
