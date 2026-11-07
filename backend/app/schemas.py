from pydantic import BaseModel

class MovieOut(BaseModel):
    id: int
    title: str
    year: int
    director: str
    genres: list[str]
    rating: float
    duration: str
    synopsis: str
    poster_url: str
    cast: list[str]