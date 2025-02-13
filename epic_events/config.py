from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///database.db"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session to interact with the database
SessionLocal = sessionmaker(bind=engine)

# Base class for our models
Base = declarative_base()
