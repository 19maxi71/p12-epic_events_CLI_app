import typer
from sqlalchemy.orm import Session
from epic_events.config import SessionLocal
from epic_events.crud import (
    add_client, get_all_clients, add_contract, get_all_contracts, 
    add_event, get_all_events, create_user, authenticate_user
)
from epic_events.models import User

app = typer.Typer()  # Initialize Typer app

def get_db():
    """Get a new database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()