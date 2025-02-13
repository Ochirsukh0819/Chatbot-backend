from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

USER_DATABASE_URL = os.getenv("USER_DATABASE_URL")

engine = create_engine(USER_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False , bind=engine)

Base = declarative_base() 


