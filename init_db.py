from epic_events.config import Base, engine
from epic_events.models import User, Role, Client, Contract, Event

def init_database():
    """Initialize the database with required tables."""
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")