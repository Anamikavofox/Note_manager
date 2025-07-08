from sqlalchemy import Column,Integer,String,Float,DateTime
from app.database import Base
from datetime import datetime


class Weather(Base):
    __tablename__="weather"

    id = Column(Integer, primary_key=True, index=True)
    place = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    temperature = Column(Float)
    weather = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

