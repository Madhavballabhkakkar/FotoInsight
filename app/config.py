"""Read configuration from the environment. Secrets stay in .env, not in git."""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "fotoinsight")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "fotoinsight")
    # Cloud MySQL hosts (Aiven, Railway, TiDB, etc.) usually need TLS.
    MYSQL_SSL = os.environ.get("MYSQL_SSL", "0") == "1"
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
    MYSQL_DATABASE = os.environ.get("MYSQL_TEST_DATABASE", "fotoinsight_test")
