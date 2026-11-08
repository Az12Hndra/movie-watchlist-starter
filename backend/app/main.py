from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="FilmLog API")

from app.routers import auth, movies, watched, watchlist

# This is how frontend talk to the server (CORS)
# For security note, I list the exact frontend address instead of "*" which means anyone.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers,
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(part) for part in first["loc"] if part!= "body")
    return JSONResponse(
        status_code=400,
        content={"error": f"Invalid input ({field}): {first['msg']}"},
    )

app.include_router(movies.router)
app.include_router(auth.router)
app.include_router(watchlist.router)
app.include_router(watched.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Note: The validation handler uses only the field name and the short message.
# FastAPI's raw error list also contains the input value, which for a failed registration could be the user's password.