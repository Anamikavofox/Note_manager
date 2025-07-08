from fastapi import HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List,Optional

from app.database import SessionLocal
from app.schemas import Note, NoteOut
from app.routers.user import get_current_user


router = APIRouter(prefix="/notes", tags=["notes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/notes/",response_model=NoteOut,status_code=201)
def create_note(note:Note,db:Session=Depends(get_db), user=Depends(get_current_user)):
    sql = text("""
        insert into notes (title, content, user_id)
        values (:title, :content, :user_id)
        returning *
               """)
    result = db.execute(sql, {"title": note.title, "content": note.content, "user_id": user.id})
    db.commit()
    row=result.fetchone()
    return NoteOut(**dict(row._mapping))


@router.get("/notes/",response_model=list[NoteOut])
def get_notes(db: Session = Depends(get_db),user=Depends(get_current_user)):
    sql=text("select * from notes where user_id=:user_id")
    rows=db.execute(sql,{"user_id":user.id}).fetchall()
    return [NoteOut(**dict(row._mapping)) for row in rows]
    

@router.get("/notes/{note_id}",response_model=NoteOut)
def get_note(note_id:int,db: Session = Depends(get_db),user=Depends(get_current_user)):
    sql=text("select * from notes where id=:id and user_id=:user_id")
    row=db.execute(sql,{"id":note_id,"user_id":user.id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut(**dict(row._mapping))


@router.put("/notes/update",response_model=List[NoteOut])
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


@router.delete("/notes/delete", status_code=204)
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
