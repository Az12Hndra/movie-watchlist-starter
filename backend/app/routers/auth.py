import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.deps import get_current_user
from app.schemas import LoginIn, LoginOut, RegisterIn, UserOut
from app.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)

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
            (data.username, data.email, password_hash)
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username is already registered")

    return {"id": cursor.lastrowid, "username": data.username, "email": data.email}

# Note: The error message doesn't say which of email or username was taken, so it reveals a little less to attackers

@router.post("/login", response_model=LoginOut)
def login(data: LoginIn, db: sqlite3.Connection = Depends(get_db)):
    user = db.execute(
        "SELECT id, username, email, password_hash FROM users WHERE email = ?",
        (data.email,),
    ).fetchone()

    # So it always run one password check, even for unknown emails
    password_hash = user["password_hash"] if user else DUMMY_HASH
    password_ok = verify_password(data.password, password_hash)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user["id"])
    return {
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]},
    }

@router.get("/me", response_model=UserOut)
def me(current_user: sqlite3.Row = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
    }