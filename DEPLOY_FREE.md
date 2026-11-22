# Free live hosting (no MySQL)

FotoInsight uses **SQLite** (a local file) plus optional **Firebase** cloud sync.
You no longer need Aiven or any cloud MySQL.

## Option A · Render (simple)

1. Push this repo to GitHub (already at https://github.com/Madhavballabhkakkar/FotoInsight)
2. Render → New Web Service → connect the repo
3. Build: `pip install -r requirements.txt && python database/seed_data.py --reset`
4. Start: `gunicorn -w 1 -b 0.0.0.0:$PORT "wsgi:app"`
5. Env vars:
   - `APP_ENV=production`
   - `SECRET_KEY=` (any long random string)
   - `SQLITE_PATH=instance/fotoinsight.db`
6. Deploy → open `https://YOUR-SERVICE.onrender.com`

Admin: `admin` / `Admin@123`

## Option B · PythonAnywhere

1. Free account at https://www.pythonanywhere.com/
2. Bash:

```bash
git clone https://github.com/Madhavballabhkakkar/FotoInsight.git
cd FotoInsight
python3.10 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python database/seed_data.py --reset
```

3. Web → Manual config → Python 3.10  
4. Virtualenv: `/home/YOUR_USERNAME/FotoInsight/venv`  
5. Paste `pythonanywhere_wsgi.py` (replace YOUR_USERNAME)  
6. Static files: `/static/` → `/home/YOUR_USERNAME/FotoInsight/app/static/`  
7. Reload → `https://YOUR_USERNAME.pythonanywhere.com`
