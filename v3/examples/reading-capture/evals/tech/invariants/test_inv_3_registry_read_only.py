"""Invariant: INV-3 — Only app/integrations/registry/ calls the Asset Registry, and only with GET.
Fails when: the registry client contains a write method call, or the registry host appears outside the client.
Live from: the unit that builds app/integrations/registry/.
"""
import pathlib
import re

APP = pathlib.Path("app")
CLIENT = APP / "integrations" / "registry"
WRITES = re.compile(r"\.(post|put|patch|delete)\(", re.I)


def test_inv_3_registry_client_only_reads():
    for f in CLIENT.rglob("*.py") if CLIENT.exists() else []:
        hit = WRITES.search(f.read_text())
        assert hit is None, f"{f}: the registry client makes a write call ({hit.group(0)})"


def test_inv_3_registry_host_only_in_the_client():
    for f in APP.rglob("*.py") if APP.exists() else []:
        if CLIENT in f.parents:
            continue
        assert "REGISTRY_BASE_URL" not in f.read_text(), f"{f}: talks to the Asset Registry outside the client"
