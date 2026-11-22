"""One row of public business details. Prices and services live in their own tables."""

from app.db import execute, query_one
from app.utils import clean_row

DEFAULTS = {
    "business_name": "FotoInsight Studio",
    "tagline": "Wedding, celebration, and film — planned with care.",
    "email": "hello@fotoinsight.demo",
    "phone": "+91 00000 00000",
    "address": "Sample Studio Address",
    "city": "Jaipur",
    "map_lat": 26.9124,
    "map_lng": 75.7873,
    "instagram_url": "https://instagram.com",
    "facebook_url": "https://facebook.com",
    "youtube_url": "https://youtube.com",
    "about_intro": "",
    "mission": "",
    "vision": "",
}


def get():
    row = clean_row(query_one("SELECT * FROM business_settings WHERE id = 1"))
    if not row:
        return dict(DEFAULTS)
    return row


def update(data):
    execute(
        """
        UPDATE business_settings SET
            business_name=%s, tagline=%s, email=%s, phone=%s, address=%s, city=%s,
            map_lat=%s, map_lng=%s, instagram_url=%s, facebook_url=%s, youtube_url=%s,
            about_intro=%s, mission=%s, vision=%s
        WHERE id = 1
        """,
        (
            data["business_name"], data["tagline"], data["email"], data["phone"], data["address"], data["city"],
            data["map_lat"], data["map_lng"], data["instagram_url"], data["facebook_url"], data["youtube_url"],
            data["about_intro"], data["mission"], data["vision"],
        ),
    )
