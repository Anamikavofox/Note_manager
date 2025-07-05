import os,requests
from celery_app import celery_app
from database import SessionLocal
from models import Weather
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("OPENWEATHER_API_KEY")

@celery_app.task(name="tasks.fetch_vofox_weather")
def fetch_vofox_weather(place:"Vofox",lat=9.9312, lon =76.2673):
    url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response=requests.get(url)

    if response.status_code!=200:
        return{"error":"Failed to fetch weather data"}
    
    data=response.json()
    session=SessionLocal()
    try:
        weather=Weather(
            place=place,
            lat=lat,
            lon=lon,
            temperature=data["main"]["temp"],
            weather=data["weather"][0]["main"],
            description=data["weather"][0]["description"]
        )
        session.add(weather)
        session.commit()
        return{"status":"Weather data stored"}
    finally:
        session.close()