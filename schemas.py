from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class Note(BaseModel):
    title: str
    content: str


class NoteOut(Note):
    id: int

class VerificationInput(BaseModel):
    username: str
    code: str    

class Config:
    orm_mode = True
