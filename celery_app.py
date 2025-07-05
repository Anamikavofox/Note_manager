from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL=os.getenv("REDIS_URL")

celery_app=Celery("weather_tasks",
                  broker=REDIS_URL,include=["tasks"])


celery_app.conf.timezone='Asia/Kolkata'

celery_app.conf.beat_schedule={"Fetch-weather-every-5-minutes":
                               {"task":"tasks.fetch_vofox_weather",
                                                                "schedule":crontab(minute="*/5"),
                                                                "args":("Vofox", 9.9312, 76.2673)}}

