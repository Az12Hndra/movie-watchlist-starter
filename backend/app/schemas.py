from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

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

class RegisterIn(BaseModel):

    # If someone sends a field that doesn't defined ("role":"admin", "id":1), the request is rejected
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_,+-]+$")

    # Hashing is slow, so without a cap, an attacker could send a various MB of password and burn down the CPU
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

# UserOut has no password_hash field, so it can never be sent back even by mistake
class UserOut(BaseModel):
    id: int
    username: str
    email: str

class LoginIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

class LoginOut(BaseModel):
    token: str
    user: UserOut

class WatchlistAddIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_id: int | None = Field(default=None, ge=1)
    movieId: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def resolve_movie_id(self):
        ids = {v for v in (self.movie_id, self.movieId) if v is not None}
        if len(ids) != 1:
            raise ValueError("movie_id is required (and movieId must match it if both are sent)")
        self.movie_id = ids.pop()
        return self

class WatchedIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    movie_id: int | None = Field(default=None, ge=1)
    movieId: int | None = Field(default=None, ge=1)
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(default=None, max_length=2000)
    opinion: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def normalize(self):
        ids = {v for v in (self.movie_id, self.movieId) if v is not None}
        if len(ids) != 1:
            raise ValueError("movie_id is required (and movieId must match it if both are sent)")
        self.movie_id = ids.pop()
        self.review = (self.review or self.option) or None
        return self

class WatchlistItemOut(BaseModel):
    movie_id: int
    created_at: str
    movie: MovieOut

class WatchedItemOut(BaseModel):
    id: int
    movie_id: int
    rating: int
    review: str | None
    created_at: str
    movie: MovieOut

class RecommendIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    prompt: str | None = Field(default=None, max_length=500)
    query: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def resolve_prompt(self):
        text = self.prompt or self.query or self.description
        if not text or len(text) < 3:
            raise ValueError("prompt is required (3 to 500 characters)")
        self.prompt = text
        return self

class GeminiPick(BaseModel):
    movie_id: int
    reasoning: str

class RecommendOut(BaseModel):
    movie_id: int
    reasoning: str
    movie: MovieOut