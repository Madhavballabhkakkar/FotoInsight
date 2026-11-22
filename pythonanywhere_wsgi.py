"""
Copy this into the PythonAnywhere Web tab → WSGI configuration file.
Replace YOUR_USERNAME with your PythonAnywhere username.
"""

import os
import sys

PROJECT_HOME = "/home/YOUR_USERNAME/FotoInsight"

if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

# Load .env from the project folder
from dotenv import load_dotenv

load_dotenv(os.path.join(PROJECT_HOME, ".env"))

os.environ.setdefault("APP_ENV", "production")

from app import create_app
from app.config import ProductionConfig

application = create_app(ProductionConfig)
