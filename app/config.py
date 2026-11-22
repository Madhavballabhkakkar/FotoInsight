"""Read configuration from the environment. Secrets stay in .env, not in git."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLITE_PATH = os.environ.get("SQLITE_PATH", str(ROOT / "instance" / "fotoinsight.db"))
    # Firebase Realtime Database REST API (compulsory cloud sync).
    FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL", "").rstrip("/")
    FIREBASE_AUTH_TOKEN = os.environ.get("FIREBASE_AUTH_TOKEN", "")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    JSON_SORT_KEYS = False
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestConfig(Config):
    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret"
    SQLITE_PATH = str(ROOT / "instance" / "fotoinsight_test.db")
