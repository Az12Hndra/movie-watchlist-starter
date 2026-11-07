import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas import RegisterIn, UserOut
from app.security import hash_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: sqlite3.Connection = Depends(get_db)):
    taken_user = db.execute(
        "SELECT 1 FROM users WHERE email = ? OR username = ?",
        (data.email, data.username),
    ).fetchone()
    if taken_user:
        raise HTTPException(status_code=409, detail="Email or username is already registered")

    password_hash = hash_password(data.password)

    try:
        cursor = db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (data.username, data.email, data.password)
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username is already registered")

    return {"id": cursor.lastrowid, "username": data.username, "email": data.email}

# Note: The error message doesn't say which of email or username was taken, so it reveals a little less to attackers