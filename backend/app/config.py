import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

# Absolute backend/ directory. Relative SQLite URLs and the .env file are
# anchored here so the app behaves identically no matter which directory it
# is launched from (repo root, backend/, an IDE, a service manager, ...).
BACKEND_DIR = Path(__file__).resolve().parent.parent


def resolve_database_url(url: str) -> str:
    """Normalize a DATABASE_URL for SQLAlchemy.

    - Render/Heroku hand out ``postgres://`` URLs, which SQLAlchemy 2.x
      rejects outright ("Can't load plugin: sqlalchemy.dialects:postgres").
      They are rewritten to ``postgresql+psycopg2://`` so production starts
      without config hacks. The explicit ``+psycopg2`` driver matters:
      SQLAlchemy 2.1 resolves a bare ``postgresql://`` to the psycopg *v3*
      dialect, while this project ships psycopg2-binary - a bare
      ``postgresql://`` would crash with ``No module named 'psycopg'``.
      Bare ``postgresql://`` URLs are pinned to psycopg2 for the same reason.
    - Relative ``sqlite:///`` URLs are anchored to backend/ so local
      development behaves the same no matter where the server was launched.

    Every other URL passes through untouched.
    """
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url
    path = url[len(prefix):]
    if not path or path == ":memory:":
        return url
    db_path = Path(path)
    if db_path.is_absolute():
        return url
    return f"{prefix}{(BACKEND_DIR / db_path).resolve().as_posix()}"


# Environments where the placeholder SECRET_KEY is tolerated. Anything else
# (staging, production, ...) must supply a real secret or startup fails below.
DEV_ENVIRONMENTS = {"development", "dev", "local", "test", "testing"}

# Known placeholder secrets (current and historical) that must never be used
# outside local development.
PLACEHOLDER_SECRET_MARKERS = (
    "change-me",
    "dev-only-insecure",
    "dualwell-super-secret",
)


class Settings(BaseSettings):
    PROJECT_NAME: str = "DualWell: Smart Student Wellness and Academic Performance System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    # Placeholder only: override via backend/.env (or an env var) before any
    # real deployment. Never ship a real secret in code. Refused outside
    # development by validate_secret_key() below.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-insecure-secret-key-change-me")
    ALGORITHM: str = "HS256"
    # Short-lived access token; clients renew it via POST /api/auth/refresh.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Failed-login rate limiting (sliding window, in-memory per process).
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 300

    # SQLite default, easily swapped with a PostgreSQL URL. Relative sqlite
    # paths are anchored to backend/ by app.database.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dualwell.db")

    # Set to false (e.g. in tests) to skip seeding the demo persona on startup.
    SEED_ON_STARTUP: bool = True

    # CORS: comma-separated allowed browser origins from the environment,
    # e.g. CORS_ORIGINS=https://gayathrimarimuthu252008-star.github.io
    # When unset/empty, parse_cors_origins() falls back to the localhost
    # origins so local development is unchanged.
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "")

    # Wearable config stubs
    FITBIT_CLIENT_ID: str = os.getenv("FITBIT_CLIENT_ID", "")
    FITBIT_CLIENT_SECRET: str = os.getenv("FITBIT_CLIENT_SECRET", "")

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        extra = "ignore"


# Origins allowed when CORS_ORIGINS is not set (local development only).
DEFAULT_LOCAL_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]


def parse_cors_origins(raw: str) -> List[str]:
    """Parse the comma-separated CORS_ORIGINS value into exact origins.

    Entries are trimmed and trailing slashes dropped so
    ``https://user.github.io/`` matches the browser's Origin header
    ``https://user.github.io`` (origins never carry a path). An empty value
    returns the localhost origins, keeping local development unchanged.
    """
    if not raw or not raw.strip():
        return list(DEFAULT_LOCAL_ORIGINS)
    origins = []
    for entry in raw.split(","):
        origin = entry.strip().rstrip("/")
        if origin:
            origins.append(origin)
    return origins


def validate_secret_key(cfg: "Settings") -> None:
    """Fail fast when a placeholder SECRET_KEY is used outside development."""
    if cfg.ENVIRONMENT.strip().lower() in DEV_ENVIRONMENTS:
        return
    secret = cfg.SECRET_KEY or ""
    looks_placeholder = (
        len(secret) < 32
        or any(marker in secret.lower() for marker in PLACEHOLDER_SECRET_MARKERS)
    )
    if looks_placeholder:
        raise RuntimeError(
            f"Refusing to start: SECRET_KEY is missing or still a placeholder while "
            f"ENVIRONMENT='{cfg.ENVIRONMENT}'. Generate one with "
            f"`python -c \"import secrets;print(secrets.token_urlsafe(48))\"` and set it "
            f"in backend/.env (or the environment) before running in this environment."
        )


settings = Settings()
validate_secret_key(settings)
