from sqlalchemy import create_engine,Column,Integer,String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

DATABASE_URL="postgresql://anamika_ks:Anamika%4002@localhost:5432/notesdb"

engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

Base=declarative_base()

class NoteModel(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"))
    user=relationship("UserModel",back_populates="notes")