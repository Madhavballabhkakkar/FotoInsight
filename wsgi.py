"""WSGI entry used by Render (Gunicorn) and other hosts."""

import os

os.environ.setdefault("APP_ENV", "production")

from app import create_app
from app.config import ProductionConfig

app = create_app(ProductionConfig)
