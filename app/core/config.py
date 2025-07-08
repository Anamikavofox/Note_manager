import os
from dotenv import load_dotenv

class WeatherConfig:
    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.units = "metric"
        self.default_place = "Vofox"
        self.default_lat = 9.9312
        self.default_lon = 76.2673
        self.redis_url = os.getenv("REDIS_URL")

        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY is missing from .env")
        if not self.redis_url:
            raise ValueError("REDIS_URL is missing from .env")
        
    def build_url(self, lat=None, lon=None, units=None):
        lat = lat or self.default_lat
        lon = lon or self.default_lon
        units = units or self.units
        return f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}&units={units}"
