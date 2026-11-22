"""Start FotoInsight.

Local use:
    python run.py

Production:
    APP_ENV=production gunicorn -w 2 -b 0.0.0.0:8000 "run:app"
"""

import os

from app import create_app
from app.config import Config, ProductionConfig

app = create_app(ProductionConfig if os.environ.get("APP_ENV") == "production" else Config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=app.config.get("DEBUG", False))
