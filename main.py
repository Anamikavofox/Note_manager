from fastapi import FastAPI,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional,List
from jose import JWTError,jwt

from database import Base,engine,SessionLocal,NoteModel
from models   import UserModel
from auth import hash_pw, verify_pw, create_token, SECRET_KEY, ALGORITHM
from schemas import Note, NoteOut, UserIn, Token

Base.metadata.create_all(bind=engine)

app= FastAPI()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    user=db.query(UserModel).filter(UserModel.username==username).first()

    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    return user


@app.post("/register",status_code=201)
def register(user:UserIn,db:Session=Depends(get_db)):
    if db.query(UserModel).filter(UserModel.username==user.username).first():
        raise HTTPException(400,"username already exists")
    db_user=UserModel(username=user.username,password=hash_pw(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return{"id":db_user.id,"username":db_user.username}

@app.post("/login",response_model=Token)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(UserModel).filter(UserModel.username==form.username).first()
    if not user or not verify_pw(form.password,user.password):
        raise HTTPException(401,"Invalid credentials")
    token=create_token(user.username)
    return {"access_token":token,"token_type":"bearer"}

@app.post("/notes/",response_model=NoteOut,status_code=201)
def create_note(note:Note,db:Session=Depends(get_db), user=Depends(get_current_user)):
    db_note=NoteModel(title=note.title,content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@app.get("/notes/",response_model=list[NoteOut])
def get_notes(db: Session = Depends(get_db),user=Depends(get_current_user)):
    return db.query(NoteModel).all()


@app.get("/notes/{note_id}",response_model=NoteOut)
def get_note(note_id:int,db: Session = Depends(get_db),user=Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/update",response_model=List[NoteOut])
def update_note(updated_note:Note,
                note_id:Optional[int]=None,
                title:Optional[str]=None,
                db: Session = Depends(get_db),
                username:str=Depends(get_current_user)):
    
    if note_id is None and title is None:
        raise HTTPException(status_code=400,detail="Provide note_id or title to locate the note")
    
    filters = []
    if note_id is not None:
        filters.append(NoteModel.id == note_id)
    if title is not None:
        filters.append(NoteModel.title == title)

    note=db.query(NoteModel).filter(or_(*filters)).all()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for n in note:
        n.title=updated_note.title
        n.content=updated_note.content
    db.commit()
    for n in note:
        db.refresh(n)
    return note


@app.delete("/notes/delete", status_code=204)
def delete_note_by_any_field(
    note_id: int = None,
    title: str = None,
    content: str = None,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    if note_id is None and title is None and content is None:
        raise HTTPException(status_code=400, detail="At least one field (id, title, or content) must be provided.")

    filters = []
    if note_id is not None:
        filters.append(NoteModel.id== note_id)
    if title is not None:
        filters.append(NoteModel.title== title)
    if content is not None:
        filters.append(NoteModel.content== content)

    deleted = db.query(NoteModel).filter(or_(*filters)).delete(synchronize_session=False)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="No matching note found")

    db.commit()
    return
