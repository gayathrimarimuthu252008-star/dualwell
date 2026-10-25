import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

# Absolute backend/ directory. Relative SQLite URLs and the .env file are
# anchored here so the app behaves identically no matter which directory it
# is launched from (repo root, backend/, an IDE, a service manager, ...).
BACKEND_DIR = Path(__file__).resolve().parent.parent


def resolve_database_url(url: str) -> str:
    """Anchor relative sqlite:/// URLs to backend/, leaving others untouched."""
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

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    # Wearable config stubs
    FITBIT_CLIENT_ID: str = os.getenv("FITBIT_CLIENT_ID", "")
    FITBIT_CLIENT_SECRET: str = os.getenv("FITBIT_CLIENT_SECRET", "")

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        extra = "ignore"


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
