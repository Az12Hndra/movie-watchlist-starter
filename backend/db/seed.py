import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "backend" / "filmlog.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")
MOVIES_PATH = ROOT / "data" / "movies.json"

def main():
    conn = sqlite3.connect(DB_PATH)

    # Foreign key constraints in SQLite are disabled by default.
    # This design choice is made for backwards compatibility with older databases
    # that were created before foreign key support was introduced.
    conn.execute("PRAGMA foreign_keys = ON")

    # Create the tables
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    # Read the movie data
    movies  = json.loads(MOVIES_PATH.read_text(encoding="utf-8"))

    # Insert each movie
    for m in movies:
        minutes = int(m["duration"].split()[0])
        conn.execute(
            """
            INSERT OR IGNORE INTO movies (id, title, year, director,
            genres, rating, duration_minutes, synopsis, poster_url, cast_members)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                m["id"], m["title"], m["year"], m["director"],
                json.dumps(m["genres"], ensure_ascii=False),
                m["rating"], minutes, m["synopsis"], m["poster_url"],
                 json.dumps(m["cast"], ensure_ascii=False),
            ),
        )

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    print(f"Finished. Movie in database: {count}")
    conn.close()

if __name__ == "__main__":
    main()