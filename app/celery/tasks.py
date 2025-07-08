import requests
from datetime import datetime
import pytz
from app.celery.celery__app import celery_app
from app.database import SessionLocal
from app.models import Weather
from sqlalchemy import text
from app.core.config import WeatherConfig

config=WeatherConfig()

@celery_app.task(name="app.celery.tasks.fetch_vofox_weather")
def fetch_vofox_weather(place:str=config.default_place,
                        lat:float=config.default_lat,
                        lon:float=config.default_lon):
    url=config.build_url(lat,lon)
    response=requests.get(url)

    if response.status_code!=200:
        return{"error":"Failed to fetch weather data"}
    
    data=response.json()

    india = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(india)

    session=SessionLocal()
    try:
        weather=Weather(
            place=place,
            lat=lat,
            lon=lon,
            temperature=data["main"]["temp"],
            weather=data["weather"][0]["main"],
            description=data["weather"][0]["description"],
            timestamp=now_ist
        )
        session.add(weather)
        session.commit()
        return{"status":"Weather data stored"}
    finally:
        session.close()

@celery_app.task(name="app.celery.tasks.send_heat_alert")
def send_heat_alert(place:str=config.default_place,
                    lat:float=config.default_lat,
                    lon:float=config.default_lon):
    session=SessionLocal()
    
    try:
        query = text("""
            SELECT temperature, timestamp
            FROM weather
            WHERE place = :place
            ORDER BY timestamp DESC
            LIMIT 1 """)

        result=session.execute(query,{"place":place}).fetchone()
    
        if not result:
            return {"error": "No weather data found in DB"}
        
        temperature,timestamp=result

        if temperature>32:
            print(f"Heat alert in {place},Current temperature:{temperature}°C")

        return {"status":"checked for heat alert","temperature":temperature,"timestamp":str(timestamp)}
    finally:
        session.close()