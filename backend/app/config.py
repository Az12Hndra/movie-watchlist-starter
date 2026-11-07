import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "")
if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY is missing or too short (need at least 32 characters)."
        "Set it in backend/.env"
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60