# Deploy FotoInsight on Render (free)

Render runs the Flask app with Gunicorn. MySQL is separate and free via Aiven (or similar).

## 1. Create free MySQL (Aiven)

1. Sign up at https://aiven.io/
2. Create a **MySQL** service on the free plan
3. Open the service → copy host, port, user, password, database name
4. Set SSL on (Aiven requires it)

## 2. Seed the database from your laptop

Put the Aiven values in `.env`:

```bash
MYSQL_HOST=...
MYSQL_PORT=...
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_DATABASE=defaultdb
MYSQL_SSL=1
SECRET_KEY=any-long-random-string
APP_ENV=development
```

Then:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python database/seed_data.py --reset
```

Demo logins after seed: `admin` / `Admin@123`

## 3. Push this project to GitHub

```bash
gh repo create FotoInsight --private --source=. --remote=origin --push
```

Or create a repo on github.com and push manually.

## 4. Create the Render web service

1. Go to https://dashboard.render.com/
2. **New** → **Web Service** → connect the GitHub repo
3. Settings:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn -w 1 -b 0.0.0.0:$PORT "wsgi:app"`
   - **Instance type:** Free
4. Environment variables:

| Key | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `SECRET_KEY` | long random string |
| `MYSQL_HOST` | from Aiven |
| `MYSQL_PORT` | from Aiven |
| `MYSQL_USER` | from Aiven |
| `MYSQL_PASSWORD` | from Aiven |
| `MYSQL_DATABASE` | from Aiven (often `defaultdb`) |
| `MYSQL_SSL` | `1` |

5. Deploy. Your URL will look like `https://fotoinsight.onrender.com`

## Notes for viva

- Free Render apps sleep after ~15 minutes idle. The first open can take 30–60 seconds.
- `/health` should return `{"ok": true, "database": "up"}` when MySQL is connected.
- Image uploads on Render’s free disk are not permanent; seed images are enough for the demo.
