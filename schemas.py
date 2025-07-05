from pydantic import BaseModel
from datetime import datetime


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


class WeatherResponse(BaseModel):
    place: str
    lat: float
    lon: float
    temperature:float
    weather:str
    description:str
    timestamp: datetime
  
class WeatherRequest(BaseModel):
    place: str
    lat: float
    lon: float

    class Config:
        orm_mode = True
