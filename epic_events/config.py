from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Database configuration
DATABASE_URL = "sqlite:///database.db"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session to interact with the database
SessionLocal = sessionmaker(bind=engine)

# Base class for our models
Base = declarative_base()

# Sentry configuration
sentry_sdk.init(
    dsn="https://c6ea73245c85f7f24dc205bd2844a5e8@o4508885632090112.ingest.de.sentry.io/4508885635235920",
    traces_sample_rate=1.0,
    enable_tracing=True,
    integrations=[
        SqlalchemyIntegration(),
    ],
    environment="development",
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

def slow_function():
    import time
    time.sleep(0.1)
    return "done"

def fast_function():
    import time
    time.sleep(0.05)
    return "done"

# Manually call start_profiler and stop_profiler
# to profile the code in between
sentry_sdk.profiler.start_profiler()
for i in range(0, 10):
    slow_function()
    fast_function()
#
# Calls to stop_profiler are optional - if you don't stop the profiler, it will keep profiling
# your application until the process exits or stop_profiler is called.
sentry_sdk.profiler.stop_profiler()