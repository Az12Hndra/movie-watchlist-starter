import json
import sqlite3

def to_iso(timestamp: str) -> str:
    """SQLite stores UTC as 'YYYY-MM-DD HH:MM:SS'. And then turn it into an ISO string"""
    return timestamp.replace(" ", "T") + "Z"

def row_to_movie(row: sqlite3.Row) -> dict:
    """Turn a database row into the shape the frontend expects"""
    return {
        "id": row["id"],
        "title": row["title"],
        "year": row["year"],
        "director": row["director"],
        "genres": json.loads(row["genres"]),
        "rating": row["rating"],
        "duration": f'{row["duration_minutes"]} min',
        "synopsis": row["synopsis"],
        "poster_url": row["poster_url"],
        "cast": json.loads(row["cast_members"]),
    }