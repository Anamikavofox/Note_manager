from sqlalchemy import Column,Integer,String,ForeignKey,Boolean
from sqlalchemy.orm import relationship
from database import Base

class UserModel(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    is_verified = Column(Boolean, default=False) 
    verification_code = Column(String, nullable=True)
    notes=relationship("NoteModel",back_populates="user")
