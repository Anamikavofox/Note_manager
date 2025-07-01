from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserModel(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    notes=relationship("NoteModel",back_populates="user")
