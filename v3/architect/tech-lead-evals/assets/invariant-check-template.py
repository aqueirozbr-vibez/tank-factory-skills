# © 2026 Tank Factory · CC BY 4.0
"""Invariant: INV-<n> — <the statement, verbatim from TRD §4.1>.
Fails when: <the violation that turns this check red>.
Live from: <the unit or folder whose code makes this check non-vacuous>.
"""
import pathlib

TARGET = pathlib.Path("<folder the invariant guards>")


def test_inv_<n>_<slug>():
    files = list(TARGET.rglob("*.py")) if TARGET.exists() else []
    for f in files:  # nothing to violate until the folder has code
        assert "<forbidden pattern>" not in f.read_text(), f"{f}: <what was violated>"
