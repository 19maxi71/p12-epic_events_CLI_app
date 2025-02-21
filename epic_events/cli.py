import typer
from sqlalchemy.orm import Session
from epic_events.config import SessionLocal
from epic_events.crud import (
    add_client, get_all_clients, add_contract, get_all_contracts, 
    add_event, get_all_events, create_user, authenticate_user
)
from epic_events.models import User
from rich import print
from rich.console import Console
from rich.table import Table

"""Initialize the Typer app.
This is the entry point of the CLI.
"""
app = typer.Typer()  

def get_db():
    """Get a new database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
@app.command()
def register(full_name: str, email: str, password: str, role_id: int):
    """Create a new user."""
    session = next(get_db())
    create_user(session, full_name, email, password, role_id)

@app.command()
def login(email: str, password: str):
    """Authenticate a user."""
    session = next(get_db())
    user = authenticate_user(session, email, password)
    if user:
        typer.echo(f"[bold green]Logged in as: {user.full_name} (Role: {user.role.name})[/bold green]")
    else:
        typer.echo("[blink bold red]Login failed.[/blink bold red]")

@app.command()
def add_new_client(user_email: str, full_name: str, email: str, phone: str, company_name: str):
    """Add a new client (Requires Admin or Commercial role)."""
    session = next(get_db())
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        typer.echo("[blink bold red]User not found.[/blink bold red]")
        return
    add_client(session, user, full_name, email, phone, company_name)

@app.command()
def list_clients(user_email: str):
    """List all clients (Read-Only for all users)."""
    session = next(get_db())
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        typer.echo("[blink bold red]User not found.[/blink bold red]")
        return
    get_all_clients(session, user)

@app.command()
def add_new_contract(user_email: str, client_id: int, total_amount: float, amount_due: float, signed: bool = False):
    """Add a new contract (Requires Admin or Commercial role)."""
    session = next(get_db())
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        typer.echo("[blink bold red]User not found.[/blink bold red]")
        return
    add_contract(session, user, client_id, total_amount, amount_due, signed)

@app.command()
def list_contracts(user_email: str):
    """List all contracts (Read-Only for all users)."""
    session = next(get_db())
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        typer.echo("[blink bold red]User not found.[/blink bold red]")
        return
    get_all_contracts(session, user)

@app.command()
def add_new_event(user_email: str, contract_id: int, support_contact: str, start_date: str, end_date: str, location: str, attendees: int, notes: str = None):
    """Add a new event (Requires Admin, Support, or Gestion role)."""
    session = next(get_db())
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        typer.echo("[blink bold red]User not found.[/blink bold red]")
        return

    add_event(session, user, contract_id, support_contact, start_date, end_date, location, attendees, notes)

@app.command()
def list_events(user_email: str):
    """List all events (Read-Only for all users)."""
    session = next(get_db())
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        typer.echo("[blink bold red]User not found.[/blink bold red]")
        return
    get_all_events(session, user)
