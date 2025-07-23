from fastapi import HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List,Optional

from app.database import SessionLocal
from app.schemas import Note, NoteOut
from app.routers.user import get_current_user
# import logger
from app.logger import setup_logging, logger
setup_logging()

router = APIRouter(prefix="/notes", tags=["notes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/notes/",response_model=NoteOut,status_code=201)
def create_note(note:Note,db:Session=Depends(get_db), user=Depends(get_current_user)):
    logger.info("Create notes API called!")
    try:
        sql = text("""
        insert into notes (title, content, user_id)
        values (:title, :content, :user_id)
        returning *
               """)
    # logger.info(f"sample logger {sql}")
        result = db.execute(sql, {"title": note.title, "content": note.content, "user_id": user.id})
        db.commit()
        row=result.fetchone()
        logger.info(f"sample logger user id:{user.id},title :{note.title}")
        return NoteOut(**dict(row._mapping))
    except Exception as err:
        logger.exception(f"Error while creating {err}")
        raise HTTPException(status_code=500,detail="error while creating note.")
        


@router.get("/notes/",response_model=list[NoteOut])
def get_notes(db: Session = Depends(get_db),user=Depends(get_current_user)):
    logger.info("Get note API called")
    try:
        sql=text("select * from notes where user_id=:user_id")
        rows=db.execute(sql,{"user_id":user.id}).fetchall()
        logger.info(f"Retrieved {len(rows)} notes for user {user.id}")
        return [NoteOut(**dict(row._mapping)) for row in rows]
    except Exception as err:
        logger.exception("error while getting the note")
        raise HTTPException(status_code=500,detail="error while fetching note")


@router.get("/notes/{note_id}",response_model=NoteOut)
def get_note(note_id:int,db: Session = Depends(get_db),user=Depends(get_current_user)):
    logger.info("Get notes by id called:{note_id}")
    try:
        sql=text("select * from notes where id=:id and user_id=:user_id")
        row=db.execute(sql,{"id":note_id,"user_id":user.id}).fetchone()
        if not row:
            logger.warning(f"note with ID {note_id} not found")
            raise HTTPException(status_code=404, detail="Note not found")
        logger.info(f"Note with {note_id} fetched succesfully.")
        return NoteOut(**dict(row._mapping))
    except Exception as err:
        logger.exception(f"error while fetching {note_id}:{err}")
        raise HTTPException(status_code=500,detail="error while fetching note")

@router.put("/notes/update",response_model=List[NoteOut])
async def update_note(updated_note:Note,
                note_id:Optional[int]=None,
                title:Optional[str]=None,
                db: Session = Depends(get_db),
                user=Depends(get_current_user)):
    logger.info("Notes update api called")
    if note_id is None and title is None:
        logger.warning("No identifier provided for update")
        raise HTTPException(
            status_code=400,
            detail="Provide at least note_id or title to update a note.",
        )
    try:
        exists_sql=text("""select 1 from notes where user_id=:user_id and 
                    (:id is null or id=:id) and 
                    (:title is null or title=:title) 
                    LIMIT 1""")
        if not db.execute(exists_sql,{"title":title,"user_id":user.id,"id":note_id}).fetchone():
            logger.warning("no matching found for update")
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
        logger.info(f"notes updated succesfully for user {user.id}")
        return [NoteOut(**dict(row._mapping))for row in rows]
    except Exception as err:
        logger.exception(f"error while updating notes:{err}")
        raise HTTPException(status_code=500,detail="error while updating note")

@router.delete("/notes/delete", status_code=204)
def delete_note(
    note_id: int = None,
    title: str = None,
    db: Session = Depends(get_db),
    user= Depends(get_current_user)
):
    logger.info("Notes delete update api called.")
    if note_id is None and title is None:
        logger.warning("delete failed")
        raise HTTPException(status_code=400, detail="At least one field (id, title, or content) must be provided.")
    try:
        sql=text("delete from notes where user_id=:user_id and (:id is null or id=:id) and (:title is null or title=:title)")
        result=db.execute(sql,{"user_id":user.id,"id":note_id,"title":title})
        db.commit()
        if result.rowcount==0:
            logger.warning(f"no matching note found for deleting {user.id}")
            raise HTTPException(status_code=404,detail="no matching note found")
        logger.info(f"the note deleted for the user {user.id}")
    except Exception as err:
        logger.exception(f"Error while deleting note:{err}")
        raise HTTPException(status_code=500,detail="Error while deleting note")
