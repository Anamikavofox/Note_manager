from celery import Celery
from celery.schedules import crontab
from app.core.config import WeatherConfig

config=WeatherConfig()
celery_app=Celery("weather_tasks",
                  broker=config.redis_url,include=["app.celery.tasks"])

celery_app.conf.timezone='Asia/Kolkata'

celery_app.conf.beat_schedule={"Fetch-weather-every-5-minutes":
                               {"task":"app.celery.tasks.fetch_vofox_weather",
                                "schedule":crontab(minute="*/5"),
                                "args":("Vofox", 9.9312, 76.2673)},
                                                                
                                "check-heat-alert-every-10-min":
                                {"task":"app.celery.tasks.send_heat_alert",
                                 "schedule":crontab(minute="*/10"),
                                 "args":("Vofox", 9.9312, 76.2673)}}

