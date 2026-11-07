from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

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