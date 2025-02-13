import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from sqlalchemy.orm import Session
from epic_events.models import Client, Contract, Event


def get_db_session(SessionLocal):
    """Create a new database session."""
    return SessionLocal()


def add_client(session: Session, full_name: str, email: str, phone: str, company_name: str):
    """Add a new client to the database."""
    new_client = Client(
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name
    )
    session.add(new_client)
    session.commit()
    print(f"Client '{full_name}' added successfully!")
