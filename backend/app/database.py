import sqlite3
from pathlib import Path

# backend/filmlog.db 
DB_PATH = Path(__file__).resolve().parents[1] / "filmlog.db"

def get_db():

    # check_same_thread is True by default when connecting to a local SQLite database
    # Python restricts database access to the exact operating system thread that opened the connection
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Every request gets its own temporary conn that closes automatically
    # So requests don't step on each other, and connections never get left hanging open
    try:
        yield conn
    finally:
        conn.close()