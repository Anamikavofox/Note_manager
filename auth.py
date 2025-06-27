from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "change_this_to_long_random_string"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 30

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pw(raw: str) -> str:
    return pwd_ctx.hash(raw)


def verify_pw(raw: str, hashed: str) -> bool:
    return pwd_ctx.verify(raw, hashed)


def create_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
