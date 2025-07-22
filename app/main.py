from fastapi import FastAPI
from app.routers import user,notes,weather
from app.logger_config import setup_logging,logger


setup_logging()
app=FastAPI()
app.include_router(user.router)
app.include_router(notes.router)
app.include_router(weather.router)

