from fastapi import FastAPI,HTTPException,Depends,Form,APIRouter
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import JWTError,jwt

from app.database import SessionLocal
from app.auth import hash_pw, verify_pw, create_token,SECRET_KEY, ALGORITHM
from app.schemas import UserIn, Token
from app.logger import setup_logging,logger

router = APIRouter(prefix="/users", tags=["users"])

class LoginForm:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),):

        self.username = username
        self.password = password


app= FastAPI()
bearer_scheme=HTTPBearer()
router=APIRouter(prefix="/users",tags=["users"])

def get_db():
    db=SessionLocal()
    try:    
        yield db
    finally:
        db.close()

def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme),db:Session=Depends(get_db)):
    token=credentials.credentials
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    #user=db.query(UserModel).filter(UserModel.username==username).first()
    user_sql=text("select * from users where username=:username")
    user=db.execute(user_sql,{"username":username}).fetchone()
    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    return user

@router.post("/register",status_code=201)
def register(user:UserIn,db:Session=Depends(get_db)):
    logger.info("Registration done")
    check_user_sql=text("SELECT * FROM users WHERE username = :username")
    existing_user=db.execute(check_user_sql,{"username":user.username}).fetchone()
    if existing_user:
        raise HTTPException(400,"username already exists")
    
    insert_Sql=text("""INSERT INTO users (username, password)
        VALUES (:username, :password)
        RETURNING id, username""")
    result=db.execute(insert_Sql,{"username":user.username,"password":hash_pw(user.password)})
    db.commit()
    user_row=result.fetchone()
    return{"id":user_row.id,"username":user_row.username}

@router.post("/login",response_model=Token)
def login(form:LoginForm=Depends(),db:Session=Depends(get_db)):
    logger.info("Login done")
    sql=text("select * from users WHERE username = :username")
    user = db.execute(sql, {"username": form.username}).fetchone()
    if not user or not verify_pw(form.password,user.password):
        raise HTTPException(401,"Invalid credentials")
    
    token=create_token(user.username)
    return {"access_token":token,"token_type":"bearer"}
