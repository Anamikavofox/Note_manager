from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()  

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN"))


pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pw(raw: str) -> str:
    return pwd_ctx.hash(raw)


def verify_pw(raw: str, hashed: str) -> bool:
    return pwd_ctx.verify(raw, hashed)


def create_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
