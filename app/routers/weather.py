from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.schemas import WeatherResponse

router = APIRouter(prefix="/weather", tags=["weather"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/last-hour", response_model=List[WeatherResponse], name="Recent Weather")
def get_weather(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=1)
    records = text("""
        SELECT place, lat, lon, temperature, weather, description, timestamp
        FROM weather
        WHERE timestamp >= :cutoff
        ORDER BY timestamp DESC
    """)
    rows = db.execute(records, {"cutoff": cutoff}).fetchall()
    return [WeatherResponse(**dict(row._mapping)) for row in rows]
