from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL="postgresql://anamika_ks:Anamika%4002@localhost:5432/notesdb"

engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

