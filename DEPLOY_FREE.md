# Free live hosting (PythonAnywhere)

One free account gives you:

- a public website (`https://YOUR_USERNAME.pythonanywhere.com`)
- a free MySQL database

## 1. Create the free account

1. Open https://www.pythonanywhere.com/
2. Click **Pricing** → create a **Beginner (free)** account
3. Confirm your email and log in

## 2. Get free MySQL

1. In PythonAnywhere: **Databases** tab
2. Set a MySQL password (save it)
3. Click **Initialize MySQL** / create database  
   Name will look like: `YOUR_USERNAME$fotoinsight` (or create `fotoinsight`)
4. Note:
   - Host: usually `YOUR_USERNAME.mysql.pythonanywhere-services.com`
   - User: `YOUR_USERNAME`
   - Database: `YOUR_USERNAME$fotoinsight`

## 3. Upload the code (Bash console)

Open **Consoles** → **Bash**, then run:

```bash
git clone https://github.com/Madhavballabhkakkar/FotoInsight.git
cd FotoInsight
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project folder:

```bash
nano .env
```

Paste (edit the values):

```env
SECRET_KEY=put-any-long-random-string-here
MYSQL_HOST=YOUR_USERNAME.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=YOUR_USERNAME
MYSQL_PASSWORD=your-pythonanywhere-mysql-password
MYSQL_DATABASE=YOUR_USERNAME$fotoinsight
MYSQL_SSL=0
APP_ENV=production
FLASK_DEBUG=0
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

Seed demo data:

```bash
source venv/bin/activate
python database/seed_data.py --reset
```

## 4. Create the web app

1. **Web** tab → **Add a new web app** → **Manual configuration** → **Python 3.10**
2. In **Virtualenv**, set: `/home/YOUR_USERNAME/FotoInsight/venv`
3. Open the **WSGI configuration file**
4. Delete the default content
5. Paste the contents of `pythonanywhere_wsgi.py` from this repo
6. Replace every `YOUR_USERNAME` with your real username
7. Save
8. Under **Static files**, add:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/YOUR_USERNAME/FotoInsight/app/static/` |

9. Click the big green **Reload** button

## 5. Open your live site

`https://YOUR_USERNAME.pythonanywhere.com`

Admin login: `admin` / `Admin@123`

## Free-plan limits

- Site sleeps when idle; first open can be slow
- Custom domains are limited on free plan
- Enough for a college viva demo link
