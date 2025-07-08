from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")

engine=create_engine(DATABASE_URL,echo=True)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base = declarative_base()