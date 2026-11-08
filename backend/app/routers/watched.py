import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.deps import get_current_user
from app.schemas import WatchedIn, WatchedItemOut
from app.serializers import row_to_movie, to_iso

router = APIRouter(prefix="/api/watched", tags=["watched"])

WATCHED_SQL = """
    SELECT m.*,
    r.id AS review_id,
    r.rating AS user_rating,
    r.review AS review_text,
    r.created_at AS logged_at
    FROM reviews r
    JOIN movies m ON m.id = r.movie_id
    WHERE r.user_id = ?
"""

def to_item(row: sqlite3.Row) -> dict:
    return {
        "id": row["review_id"],
        "movie_id": row["id"],
        "rating": row["user_rating"],
        "review": row["review_text"],
        "created_at": to_iso(row["logged_at"]),
        "movie": row_to_movie(row),
    }

@router.get("", response_model=list[WatchedItemOut])
def get_watched(
    current_user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        WATCHED_SQL + " ORDER BY r.created_at DESC, r.id DESC",
        (current_user["id"],),
    ).fetchall()
    return [to_item(r) for r in rows]

@router.post("", response_model=WatchedItemOut, status_code=status.HTTP_201_CREATED)
def log_watched(
    data: WatchedIn,
    current_user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db), 
):
    movie = db.execute("SELECT 1 FROM movies WHERE id = ?", (data.movie_id,)).fetchone()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    try:
        db.execute(
            "INSERT INTO reviews (user_id, movie_id, rating, review) VALUES (?, ?, ?, ?)",
            (current_user["id"], data.movie_id, data.rating, data.review),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You have already logged this movie")

    row = db.execute(
        WATCHED_SQL + " AND r.movie_id = ?",
        (current_user["id"], data.movie_id),
    ).fetchone()
    return to_item(row)