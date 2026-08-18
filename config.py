from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration shared across environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    WTF_CSRF_TIME_LIMIT = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
        mysql_port = os.getenv("MYSQL_PORT", "3306")
        mysql_db = os.getenv("MYSQL_DATABASE")
        if mysql_user and mysql_password and mysql_db:
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{mysql_user}:{mysql_password}@"
                f"{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
            )
        else:
            database_path = BASE_DIR / "database" / "patient_care.db"
            database_path.parent.mkdir(parents=True, exist_ok=True)
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_path.as_posix()}"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
