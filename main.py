from fastapi import FastAPI,HTTPException,Depends,Form
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List,Optional
from jose import JWTError,jwt

from tasks import notify_note_created 
from database import SessionLocal
from auth import hash_pw, verify_pw, create_token, SECRET_KEY, ALGORITHM
from schemas import Note, NoteOut, UserIn, Token


class LoginForm:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),):

        self.username = username
        self.password = password


app= FastAPI()
bearer_scheme=HTTPBearer()


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

#@app.get("/",tags=["root"])
#def read_root()-> dict:
#    return {"message":"welcome to the Notes Manager"}

@app.post("/register",status_code=201)
def register(user:UserIn,db:Session=Depends(get_db)):
    check_user_sql=text("SELECT * FROM users WHERE username = :username")
    existing_user=db.execute(check_user_sql,{"username":user.username}).fetchone()
    if existing_user:
        raise HTTPException(400,"username already exists")
    
    insert_Sql=text("""INSERT INTO users (username, password)
        VALUES (:username, :password)
        RETURNING id, username""")
    result=db.execute(insert_Sql,{"username":user.username,"password":hash_pw})
    db.commit()
    user_row=result.fetchone()
    return{"id":user_row.id,"username":user_row.username}

@app.post("/login",response_model=Token)
def login(form:LoginForm=Depends(),db:Session=Depends(get_db)):
    sql=text("select * from users WHERE username = :username")
    user = db.execute(sql, {"username": form.username}).fetchone()
    if not user or not verify_pw(form.password,user.password):
        raise HTTPException(401,"Invalid credentials")
    
    token=create_token(user.username)
    return {"access_token":token,"token_type":"bearer"}


@app.post("/notes/",response_model=NoteOut,status_code=201)
def create_note(note:Note,db:Session=Depends(get_db), user=Depends(get_current_user)):
    sql = text("""
        insert into notes (title, content, user_id)
        values (:title, :content, :user_id)
        returning *
               """)
    result = db.execute(sql, {"title": note.title, "content": note.content, "user_id": user.id})
    db.commit()
    row=result.fetchone()

    notify_note_created.delay(user.username,note.title)

    return NoteOut(**dict(row._mapping))


@app.get("/notes/",response_model=list[NoteOut])
def get_notes(db: Session = Depends(get_db),user=Depends(get_current_user)):
    sql=text("select * from notes where user_id=:user_id")
    rows=db.execute(sql,{"user_id":user.id}).fetchall()
    return [NoteOut(**dict(row._mapping)) for row in rows]
    

@app.get("/notes/{note_id}",response_model=NoteOut)
def get_note(note_id:int,db: Session = Depends(get_db),user=Depends(get_current_user)):
    sql=text("select * from notes where id=:id and user_id=:user_id")
    row=db.execute(sql,{"id":note_id,"user_id":user.id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut(**dict(row._mapping))


@app.put("/notes/update",response_model=List[NoteOut])
async def update_note(updated_note:Note,
                note_id:Optional[int]=None,
                title:Optional[str]=None,
                db: Session = Depends(get_db),
                user=Depends(get_current_user)):
    
    if note_id is None and title is None:
        raise HTTPException(
            status_code=400,
            detail="Provide at least note_id or title to update a note.",
        )
    
    exists_sql=text("""select 1 from notes where user_id=:user_id and 
                   (:id is null or id=:id) and 
                   (:title is null or title=:title) 
                   LIMIT 1""")

    if not db.execute(exists_sql,{"title":title,"user_id":user.id,"id":note_id}).fetchone():
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_sql=text("""update notes
                    set title=:new_title,content=:new_content where
                    user_id = :user_id
                    AND (:id is NULL or id = :id)
                    AND (:title is NULL or title = :title)
                    returning * """)
    rows=db.execute(update_sql,{"new_title": updated_note.title,
                                "new_content": updated_note.content,
                                "id": note_id,
                                "title": title,
                                "user_id": user.id,
                                 }).fetchall()
    db.commit()
    return [NoteOut(**dict(row._mapping))for row in rows]


@app.delete("/notes/delete", status_code=204)
def delete_note(
    note_id: int = None,
    title: str = None,
    db: Session = Depends(get_db),
    user= Depends(get_current_user)
):
    if note_id is None and title is None:
        raise HTTPException(status_code=400, detail="At least one field (id, title, or content) must be provided.")
    sql=text("delete from notes where user_id=:user_id and (:id is null or id=:id) and (:title is null or title=:title)")
    result=db.execute(sql,{"user_id":user.id,"id":note_id,"title":title})
    db.commit()
    if result.rowcount==0:
        raise HTTPException(status_code=404,detail="no matching note found")
    return
