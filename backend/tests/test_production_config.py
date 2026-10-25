"""Production-hosting guards for Render (see QA production checklist).

Covers, in order:
  * DATABASE_URL ``postgres://`` -> ``postgresql://`` conversion (Render's
    default scheme, rejected by SQLAlchemy 2.x), SQLite untouched;
  * SECRET_KEY must refuse to start outside development when missing or
    still a placeholder;
  * CORS_ORIGINS comma-separated parsing with localhost fallback;
  * /api/health runs a real SELECT 1 and reports 200/503 accordingly.
"""
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import (
    Settings,
    parse_cors_origins,
    resolve_database_url,
    validate_secret_key,
)
from app.database import get_db
from app.main import app

GITHUB_PAGES_ORIGIN = "https://gayathrimarimuthu252008-star.github.io"
PLACEHOLDER = "dev-only-insecure-secret-key-change-me"


# ---------------------------------------------------------------- DATABASE_URL

def test_render_postgres_scheme_is_converted_to_postgresql():
    assert (
        resolve_database_url("postgres://user:pw@host:5432/dualwell")
        == "postgresql+psycopg2://user:pw@host:5432/dualwell"
    )


def test_bare_postgresql_is_pinned_to_psycopg2_driver():
    # SQLAlchemy 2.1 resolves bare postgresql:// to the psycopg3 dialect,
    # but the project ships psycopg2-binary -> must be pinned explicitly.
    assert (
        resolve_database_url("postgresql://user:pw@host:5432/dualwell")
        == "postgresql+psycopg2://user:pw@host:5432/dualwell"
    )


def test_explicit_driver_postgresql_scheme_passes_through_untouched():
    url = "postgresql+psycopg2://user:pw@host:5432/dualwell"
    assert resolve_database_url(url) == url


def test_sqlite_url_still_anchored_for_local_dev():
    resolved = resolve_database_url("sqlite:///./dualwell.db")
    assert resolved.startswith("sqlite:///")
    assert resolved.endswith("/backend/dualwell.db")
    # Absolute and in-memory SQLite URLs stay untouched.
    abs_db = Path(tempfile.gettempdir()) / "x.db"  # absolute on every OS
    abs_url = f"sqlite:///{abs_db.as_posix()}"
    assert resolve_database_url(abs_url) == abs_url
    assert resolve_database_url("sqlite:///:memory:") == "sqlite:///:memory:"


# ---------------------------------------------------------------- SECRET_KEY

def test_production_refuses_default_secret_key():
    cfg = Settings(ENVIRONMENT="production", SECRET_KEY=PLACEHOLDER)
    with pytest.raises(RuntimeError, match="Refusing to start"):
        validate_secret_key(cfg)


def test_production_refuses_missing_secret_key():
    cfg = Settings(ENVIRONMENT="production", SECRET_KEY="")
    with pytest.raises(RuntimeError, match="Refusing to start"):
        validate_secret_key(cfg)


def test_production_refuses_short_secret_key():
    cfg = Settings(ENVIRONMENT="production", SECRET_KEY="too-short-secret")
    with pytest.raises(RuntimeError, match="Refusing to start"):
        validate_secret_key(cfg)


def test_production_accepts_real_secret_key():
    validate_secret_key(Settings(ENVIRONMENT="production", SECRET_KEY="x" * 48))


def test_development_still_tolerates_default_secret_key():
    # Local development must keep working unchanged.
    validate_secret_key(Settings(ENVIRONMENT="development", SECRET_KEY=PLACEHOLDER))


# ---------------------------------------------------------------- CORS_ORIGINS

def test_cors_parses_comma_separated_origins():
    raw = f"{GITHUB_PAGES_ORIGIN}, https://example.com/"
    assert parse_cors_origins(raw) == [
        GITHUB_PAGES_ORIGIN,
        "https://example.com",  # trailing slash stripped; origins have no path
    ]


def test_cors_defaults_to_localhost_for_local_dev():
    for raw in ("", "   ", None):
        origins = parse_cors_origins(raw)
        assert "http://localhost:5173" in origins
        assert "http://127.0.0.1:3000" in origins


def test_cors_empty_entries_are_dropped():
    assert parse_cors_origins(f" , {GITHUB_PAGES_ORIGIN} ,") == [GITHUB_PAGES_ORIGIN]


# ---------------------------------------------------------------- /api/health

def test_health_runs_select_1_and_reports_connected(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"
    assert body["service"] == "DualWell API"


def test_health_reports_503_when_database_unreachable():
    """If SELECT 1 raises, /api/health must flip to 503/unavailable."""

    class BrokenDB:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("connection refused")

        def close(self):
            pass

    def broken_get_db():
        yield BrokenDB()

    app.dependency_overrides[get_db] = broken_get_db
    try:
        with TestClient(app) as test_client:
            res = test_client.get("/api/health")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert res.status_code == 503
    body = res.json()
    assert body["status"] == "degraded"
    assert body["database"] == "unavailable"
