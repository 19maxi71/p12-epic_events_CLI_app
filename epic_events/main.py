import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from epic_events.config import engine, Base
from epic_events.models import Client, Contract, Event

def setup_database():
    """Creates the database and tables."""
    Base.metadata.create_all(engine)
    print("Database updated with Contracts and Events.")

if __name__ == "__main__":
    setup_database()

