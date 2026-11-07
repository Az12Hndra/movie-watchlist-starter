import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_db
from app.schemas import MovieOut

router = APIRouter(prefix="/api/movies", tags=["movies"])

def row_to_movie(row: sqlite3.Row) -> dict:
    """Turn a database row into the shape the frontend expects."""
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

# Accepts optional URL parameters: ?genre=..., ?search=..., and ?shuffle=true
# db = Depends(get_db) asks database.py to open a database connection for this request
@router.get("", response_model=list[MovieOut])
def list_movies(
    genre: str | None = Query(default=None, max_length=50),
    search: str | None = Query(default=None, max_length=100),
    shuffle: bool = False,
    db: sqlite3.Connection = Depends(get_db),
):

    # Prepares empty list to dynamically build SQL WHERE filter clauses
    conditions = []
    params = []

    if genre:
        # If a genre filter was sent, adds a SQL check to match that genre
        conditions.append("genres LIKE ?")
        params.append(f'%"{genre}"%')
    if search:
        # If a search keyword was sent, adds a check for matching titles or directors
        conditions.append("(title LIKE ? OR director LIKE?)")
        params.extend([f"%{search}&", f"%{search}%"])

    sql = "SELECT * FROM movies"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY RANDOM()" if shuffle else " ORDER BY id"

    rows = db.execute(sql, params).fetchall()
    return [row_to_movie(r) for r in rows]

@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return row_to_movie(row)