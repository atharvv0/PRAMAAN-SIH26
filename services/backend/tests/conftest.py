"""Backend API test isolation.

services/backend/app/core/config.py defaults DATABASE_URL to a real
PostgreSQL instance (per docker-compose, on port 5433) -- appropriate for
production and for a docker-based integration test, but it means
`pytest services/backend/tests` previously could only pass on a machine that
already had that Postgres container running, with no fixture or skip-marker
making that dependency explicit. On a clean checkout (or this sandbox) every
test in this directory would fail during the FastAPI startup event
(`init_db()`) with a raw connection error before a single assertion ran.

This sets DATABASE_URL to a throwaway file-based SQLite database (module
scope, one file per test session) before `services.backend.app.core.config`
is ever imported, so the API-surface and orchestration-wiring tests in this
directory are runnable anywhere. It intentionally does NOT set this for the
whole repo (see services/conftest.py) -- only this test package needs a
database at all, and other services should not silently inherit a SQLite
override that isn't relevant to them.

This does not replace a real integration test against Postgres/Qdrant/Ollama
(see services/backend/README.md "Run it" / docker-compose.yml) -- SQLite is
close enough to validate the ORM/repository wiring and API contracts, but
Postgres-specific behaviour (true UUID column type, NUMERIC precision,
concurrent-session semantics) is not exercised here.
"""
from __future__ import annotations

import os
import tempfile

import pytest

_tmp_dir = tempfile.mkdtemp(prefix="pramaan-backend-test-db-")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir}/pramaan_test.db")


@pytest.fixture(scope="session", autouse=True)
def _run_app_lifespan():
    """Every test module in this package builds its own module-level
    `client = TestClient(app)` and calls it directly (not as a fixture), so
    none of them individually go through `with TestClient(app) as client:`.
    Starlette's TestClient only sends the ASGI lifespan startup event (which
    is what triggers app/main.py's `init_db()` -- i.e. table creation) when
    used as a context manager; a bare `TestClient(app)` never creates the
    schema, so every DB-touching test previously failed with
    "no such table: workspaces" et al. before a single assertion ran.

    Triggering startup once here, for the whole session, is sufficient:
    init_db() acts on the shared SQLite file behind the module-level engine
    singleton in app/db/database.py, so every other TestClient instance
    created afterwards can use the resulting schema even though its own
    lifespan was never entered.
    """
    from fastapi.testclient import TestClient

    from ..app.main import app

    with TestClient(app):
        yield
