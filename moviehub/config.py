import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path):
    if not env_path.exists():
        return

    with env_path.open(encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file(BASE_DIR / ".env")


def get_database_uri():
    database_uri = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if database_uri and database_uri.startswith("postgres://"):
        return database_uri.replace("postgres://", "postgresql://", 1)

    if database_uri and database_uri.startswith("sqlite:///"):
        sqlite_path = database_uri.replace("sqlite:///", "", 1)
        if not os.path.isabs(sqlite_path):
            sqlite_path = str(BASE_DIR / sqlite_path)
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        return f"sqlite:///{sqlite_path}"

    if database_uri:
        return database_uri

    database_path = BASE_DIR / "instance" / "moviehub.db"
    os.makedirs(database_path.parent, exist_ok=True)
    return f"sqlite:///{database_path}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False