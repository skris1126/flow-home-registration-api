import bcrypt
import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.config import DASHBOARD_ORIGINS, POSTGRES_DSN

PIN_PATTERN = re.compile(r"^\d{4}$")

app = FastAPI(title="Registration Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=DASHBOARD_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def get_connection() -> psycopg.Connection:
    return psycopg.connect(POSTGRES_DSN)


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=200)
    pin: str

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, value: str) -> str:
        if not PIN_PATTERN.match(value):
            raise ValueError("PIN must be exactly 4 digits")
        return value


class RegisterResponse(BaseModel):
    userId: str
    email: str
    username: str


def _hash_secret(secret: str) -> str:
    return bcrypt.hashpw(secret.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users LIMIT 1")
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest) -> RegisterResponse:
    email = request.email.lower()
    password_hash = _hash_secret(request.password)
    pin_hash = _hash_secret(request.pin)

    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            if cur.fetchone() is not None:
                raise HTTPException(status_code=409, detail="An account with this email already exists")

            cur.execute(
                """
                INSERT INTO users (email, username, password_hash, pin_hash)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id, email, username
                """,
                (email, request.username, password_hash, pin_hash),
            )
            user_id, stored_email, username = cur.fetchone()
            conn.commit()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to create account") from exc

    return RegisterResponse(userId=str(user_id), email=stored_email, username=username)
