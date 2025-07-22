from fastapi import FastAPI
from app.routers import user,notes,weather
from app.logger import setup_logging,logger

setup_logging()
app=FastAPI() 

# logger=logging.getLogger("app")
logger.info("Starting fastapi app..")

app.include_router(user.router)
app.include_router(notes.router)
app.include_router(weather.router)

