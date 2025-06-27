from fastapi import FastAPI,HTTPException,Depends,status
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
import secrets
from typing import Optional
from database import Base,engine,SessionLocal,NoteModel

Base.metadata.create_all(bind=engine)

app= FastAPI()
security=HTTPBasic()

VALID_USERNAME="admin"
VALID_PASSWORD="password"

def authenticate(credentials:HTTPBasicCredentials=Depends(security)):
    username_correct=secrets.compare_digest(credentials.username,VALID_USERNAME)
    password_correct=secrets.compare_digest(credentials.password,VALID_PASSWORD)
    if not(username_correct and password_correct):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password",
                            headers={"WWW-Authenticate":"Basic"})
    return credentials.username

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Note(BaseModel):
    title:str
    content:str

class NoteOut(Note):
    id: int

    class Config:
        orm_mode=True


@app.post("/notes/",response_model=NoteOut,status_code=201)
def create_note(note:Note,db:Session=Depends(get_db), username:str=Depends(authenticate)):
    db_note=NoteModel(title=note.title,content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@app.get("/notes/",response_model=list[NoteOut])
def get_notes(db: Session = Depends(get_db),username:str=Depends(authenticate)):
    return db.query(NoteModel).all()


@app.get("/notes/{note_id}",response_model=NoteOut)
def get_note(note_id:int,db: Session = Depends(get_db),username:str=Depends(authenticate)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}",response_model=NoteOut)
def update_note(note_id:Optional[int],
                title:Optional[str],
                updated_note:Note,
                db: Session = Depends(get_db),
                username:str=Depends(authenticate)):
    
    if note_id is None and title is None:
        raise HTTPException(status_code=400,detail="Provide note_id or title to locate the note")
    
    filters = []
    if note_id is not None:
        filters.append(NoteModel.id == note_id)
    if title is not None:
        filters.append(NoteModel.title == title)

    note=db.query(NoteModel).filter(or_(*filter)).all()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for note in notes:
        note.title=updated_note.title
        note.content=updated_note.content
    db.commit()
    db.refresh(note)
    return note


@app.delete("/notes/delete", status_code=204)
def delete_note_by_any_field(
    note_id: int = None,
    title: str = None,
    content: str = None,
    db: Session = Depends(get_db),
    username: str = Depends(authenticate)
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
