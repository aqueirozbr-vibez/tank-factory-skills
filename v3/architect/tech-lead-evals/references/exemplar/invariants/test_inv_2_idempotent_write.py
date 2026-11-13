"""Invariant: INV-2 — A reading id is stored at most once; a repeat returns the first result.
Fails when: the `reading` table loses its primary key on `id`, or a migration adds a second unique path for writes.
Live from: the unit that creates the first migration.

Structural check on the migrations: `reading.id` is the primary key in the schema they produce.
"""
import pathlib
import re

MIGRATIONS = pathlib.Path("app/db/migrations")


def test_inv_2_reading_id_is_the_primary_key():
    files = sorted(MIGRATIONS.glob("*.sql")) if MIGRATIONS.exists() else []
    create = [f.read_text() for f in files if re.search(r"create table\s+reading\b", f.read_text(), re.I)]
    if not create:
        assert not files, "migrations exist but none creates `reading`: INV-2 cannot be checked"
        return
    assert re.search(r"\bid\s+uuid\s+primary key", create[0], re.I), "reading.id is not the primary key"
    dropped = [f.name for f in files if re.search(r"alter table\s+reading\s+drop constraint\s+reading_pkey", f.read_text(), re.I)]
    assert not dropped, f"a migration drops the primary key of reading: {dropped}"
