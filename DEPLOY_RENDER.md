# Deploy FotoInsight on Render (free, no MySQL)

The app now uses **SQLite** (a file). You do not need Aiven or any cloud MySQL.

## 1. Push code to GitHub

Repo: https://github.com/Madhavballabhkakkar/FotoInsight

## 2. Create Web Service on Render

1. https://dashboard.render.com/ → **New** → **Web Service**
2. Connect **FotoInsight**
3. Settings:
   - **Build command:** `pip install -r requirements.txt && python database/seed_data.py --reset`
   - **Start command:** `gunicorn -w 1 -b 0.0.0.0:$PORT "wsgi:app"`
   - **Plan:** Free
4. Environment variables:

| Key | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `SECRET_KEY` | any long random string |
| `SQLITE_PATH` | `instance/fotoinsight.db` |
| `FIREBASE_DB_URL` | your Firebase URL (optional until sync demo) |
| `FIREBASE_AUTH_TOKEN` | optional |

5. Deploy. URL will be like `https://fotoinsight.onrender.com`

## Notes

- Free Render apps sleep after idle time; first open can be slow.
- SQLite on free Render is reset when the service is rebuilt (demo data is re-seeded by the build command).
- Admin login after seed: `admin` / `Admin@123`
