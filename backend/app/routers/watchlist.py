import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.database import get_db
from app.deps import get_current_user
from app.schemas import WatchlistAddIn, WatchlistItemOut
from app.serializers import row_to_movie, to_iso

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

WATCHLIST_SQL = """
    SELECT m.*, w.created_at AS added_at
    FROM watchlists w
    JOIN movies m ON m.id = w.movie_id
    WHERE w.user_id = ?
"""

def to_item(row: sqlite3.Row) -> dict:
    return {
        "movie_id": row["id"],
        "created_at": to_iso(row["added_at"]),
        "movie": row_to_movie(row),
    }

@router.get("", response_model=list[WatchlistItemOut])
def get_watchlist(
    current_user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        WATCHLIST_SQL + " ORDER BY w.created_at DESC, m.id",
        (current_user["id"],),
    ).fetchall()
    return [to_item(r) for r in rows]

@router.post("", response_model=WatchlistItemOut, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    data: WatchlistAddIn,
    current_user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    movie = db.execute("SELECT 1 FROM movies WHERE id = ?", (data.movie_id,)).fetchone()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    try:
        db.execute(
            "INSERT INTO watchlists (user_id, movie_id) VALUES (?, ?)",
            (current_user["id"], data.movie_id),        
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Movie is already in your watchlist")

    row = db.execute(
        WATCHLIST_SQL + " AND w.movie_id = ?",
        (current_user["id"], data.movie_id),
    ).fetchone()
    return to_item(row)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    movie_id: int,
    current_user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    cursor = db.execute(
        "DELETE FROM watchlists WHERE user_id = ? AND movie_id = ?",
        (current_user["id"], movie_id),
    )
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Movie is not in your watchlist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)