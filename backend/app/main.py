from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import movies

app = FastAPI(title="FilmLog API")

# This is how frontend talk to the server (CORS)
# For security note, I list the exact frontend address instead of "*" which means anyone.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(movies.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}