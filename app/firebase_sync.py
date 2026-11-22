"""Cloud sync through the Firebase Realtime Database REST API."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from flask import current_app

from app.errors import AppError
from app.local_store import export_all, load_bundle


def _base_url():
    url = (current_app.config.get("FIREBASE_DB_URL") or "").rstrip("/")
    if not url:
        raise AppError(
            "Firebase is not configured. Set FIREBASE_DB_URL in .env "
            "(example: https://your-project-default-rtdb.firebaseio.com)."
        )
    if not url.startswith("https://"):
        raise AppError("FIREBASE_DB_URL must start with https://")
    return url


def _auth_query():
    token = current_app.config.get("FIREBASE_AUTH_TOKEN") or ""
    if not token:
        return ""
    return "?" + urllib.parse.urlencode({"auth": token})


def _request(method, path, payload=None):
    url = f"{_base_url()}/{path.lstrip('/')}{_auth_query()}"
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AppError(f"Firebase HTTP {exc.code}: {detail or exc.reason}", status=502) from exc
    except urllib.error.URLError as exc:
        raise AppError(f"Could not reach Firebase: {exc.reason}", status=502) from exc


def push_all():
    """Export local files first, then PUT the bundle to Firebase."""
    local = export_all()
    bundle = load_bundle() or {}
    payload = {
        "synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "FotoInsight",
        "tables": bundle.get("tables", {}),
        "meta": {
            "table_count": len(local["tables"]),
            "row_counts": {item["name"]: item["rows"] for item in local["tables"]},
        },
    }
    _request("PUT", "fotoinsight.json", payload)
    return {
        "ok": True,
        "synced_at": payload["synced_at"],
        "path": "fotoinsight",
        "local": local,
        "row_counts": payload["meta"]["row_counts"],
    }


def pull_summary():
    """Read the cloud copy back through REST GET (for viva proof)."""
    data = _request("GET", "fotoinsight.json")
    if not data:
        return {"ok": True, "exists": False, "message": "No FotoInsight node found in Firebase yet."}
    meta = data.get("meta") or {}
    return {
        "ok": True,
        "exists": True,
        "synced_at": data.get("synced_at"),
        "row_counts": meta.get("row_counts") or {},
        "table_names": list((data.get("tables") or {}).keys()),
    }


def configured():
    return bool(current_app.config.get("FIREBASE_DB_URL"))
