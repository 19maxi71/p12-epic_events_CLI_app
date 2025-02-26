import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', "sqlite:///database.db")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session to interact with the database
SessionLocal = sessionmaker(bind=engine)

# Base class for our models
Base = declarative_base()

# Sentry configuration
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=1.0,
    enable_tracing=True,
    integrations=[
        SqlalchemyIntegration(),
    ],
    environment=os.getenv('ENVIRONMENT', 'development'),
    send_default_pii=True,
    _experiments={
        "profiles_sample_rate": 1.0,
    }
)

# Set default tags after initialization
sentry_sdk.set_tag("application", "epic_events")
sentry_sdk.set_tag("version", "1.0.0")

# Generator for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()