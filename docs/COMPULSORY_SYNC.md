# Compulsory local + Firebase sync

## What examiners should see

1. Log in as admin → **Data Sync**
2. Click **Export to local files**
3. Show the `/data` folder now contains `.json`, `.csv`, and `.xlsx` files
4. Configure Firebase, click **Push to Firebase**, then **Read from Firebase**

## Architecture (say this in viva)

- **MySQL** stores live office records and feeds Pandas analytics.
- **JSON / CSV / Excel** are local persistence snapshots written under `/data`.
- **Firebase Realtime Database REST API** is the cloud synchronization layer (`PUT` to upload, `GET` to read back).

## Free Firebase setup

1. Open https://console.firebase.google.com/
2. Create a project → Build → **Realtime Database** → Create database
3. Start in **test mode** for the college demo (or lock rules and use an auth token)
4. Copy the database URL, for example:
   `https://your-project-default-rtdb.asia-southeast1.firebasedatabase.app`
5. Put it in `.env`:

```env
FIREBASE_DB_URL=https://your-project-default-rtdb.asia-southeast1.firebasedatabase.app
FIREBASE_AUTH_TOKEN=
```

6. Restart the Flask app, open **Data Sync**, push and pull.
