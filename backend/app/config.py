import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "polls.db"


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DB_PATH.as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
    CORS_ORIGINS = _parse_origins(os.getenv("CORS_ORIGINS", FRONTEND_BASE_URL))

    COOKIE_NAME = os.getenv("COOKIE_NAME", "appylo_voter")
    COOKIE_MAX_AGE = 60 * 60 * 24 * 365
    COOKIE_SECURE = _as_bool(os.getenv("COOKIE_SECURE"), default=False)
    COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "Lax")

    IP_HASH_SALT = os.getenv("IP_HASH_SALT", "dev-ip-salt")
    DATA_DIR = str(BASE_DIR / "data")
