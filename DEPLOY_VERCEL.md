# Deploy FotoInsight on Vercel (free)

Vercel hosts the Flask app. MySQL must be a separate free cloud database.

**Important:** `scikit-learn` is not installed on Vercel (package size limit). The Analytics forecast section will say the library is missing. All other analytics still work with Pandas and NumPy. Install `scikit-learn` locally with `pip install -r requirements-dev.txt` if you need the forecast on your laptop.

## 1. Claim the temporary deploy (or log in)

Open the claim URL from the CLI, or:

```bash
vercel login
vercel --prod
```

## 2. Create a free MySQL database

Pick one:

- [Aiven](https://aiven.io/) free trial (MySQL)
- [Railway](https://railway.app/) MySQL
- [TiDB Cloud](https://tidbcloud.com/) serverless (MySQL-compatible)
- [FreeSQLDatabase](https://www.freesqldatabase.com/)

Create a database named `fotoinsight` (or note the name they give you).

## 3. Seed the remote database (from your laptop)

In `.env`, temporarily point at the cloud DB:

```bash
MYSQL_HOST=...
MYSQL_PORT=...
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_DATABASE=fotoinsight
MYSQL_SSL=1
```

Then:

```bash
source .venv/bin/activate
python database/seed_data.py --reset
```

## 4. Set Vercel environment variables

In the Vercel project → Settings → Environment Variables (Production):

| Name | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `SECRET_KEY` | long random string |
| `MYSQL_HOST` | your cloud host |
| `MYSQL_PORT` | usually `3306` or the port they give |
| `MYSQL_USER` | your user |
| `MYSQL_PASSWORD` | your password |
| `MYSQL_DATABASE` | `fotoinsight` |
| `MYSQL_SSL` | `1` |

Redeploy after saving env vars:

```bash
vercel --prod
```

## Notes for viva

- Demo logins stay `admin` / `Admin@123` and `employee` / `Employee@123` after seeding.
- Image uploads may not persist on Vercel (read-only filesystem). Seed / built-in images are enough for the demo.
- Analytics can be slower on the free serverless plan because of cold starts.
