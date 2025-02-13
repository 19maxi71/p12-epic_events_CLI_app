import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from epic_events.config import engine, Base, SessionLocal
from epic_events.models import Client, Contract, Event
from epic_events.crud import add_client, get_db_session

def setup_database():
    """Creates the database and tables."""
    Base.metadata.create_all(engine)
    print("Database updated with Contracts and Events.")

def test_add_client():
    session = get_db_session(SessionLocal)
    add_client(session, "User BOT", "bot.com", "0611111111", "BOT LLC")

if __name__ == "__main__":
    # setup_database()
    test_add_client()

