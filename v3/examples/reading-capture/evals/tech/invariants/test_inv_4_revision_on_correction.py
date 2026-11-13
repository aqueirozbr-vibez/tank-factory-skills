"""Invariant: INV-4 — Every change to `reading.value` writes a `reading_revision` row with the old value and the actor.
Fails when: any module other than app/readings/corrections.py updates reading.value, or that module updates it without inserting a revision.
Live from: the unit that builds corrections in app/readings/.
"""
import pathlib
import re

APP = pathlib.Path("app")
OWNER = APP / "readings" / "corrections.py"
UPDATE = re.compile(r"update\s+reading\s+set\s+value|\.value\s*=\s*(?!=)", re.I)


def test_inv_4_only_corrections_changes_a_value():
    for f in APP.rglob("*.py") if APP.exists() else []:
        if f == OWNER or "migrations" in f.parts:
            continue
        assert not re.search(r"update\s+reading\s+set\s+value", f.read_text(), re.I), \
            f"{f}: changes reading.value outside corrections.py"


def test_inv_4_corrections_writes_a_revision():
    if not OWNER.exists():
        return  # nothing to violate yet
    src = OWNER.read_text()
    assert UPDATE.search(src), "corrections.py no longer changes the value: update this check with the TRD"
    assert "reading_revision" in src, "corrections.py changes a value without writing reading_revision"
