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
from epic_events.auth import ( 
    set_current_user, get_current_user, clear_current_user, 
    create_token, save_token
)
from datetime import datetime
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
        token = create_token(user.email, user.role.name)
        save_token(token)
        typer.echo(f"[bold green]Logged in as: {user.full_name} (Role: {user.role.name})[/bold green]")
    else:
        typer.echo("[bold red]Login failed.[/bold red]")

@app.command()
def logout():
    """Logout current user"""
    clear_current_user()
    typer.echo("[bold green]Logged out successfully![/bold green]")

@app.command()
def add_new_client(
    full_name: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    phone: str = typer.Option(..., prompt=True),
    company_name: str = typer.Option(..., prompt=True)
):
    """Add a new client (Requires Admin or Commercial role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        typer.echo("[bold red]Please login first: epic-events login[/bold red]")
        return
        
    add_client(session, user, full_name, email, phone, company_name)

@app.command()
def list_clients():
    """List all clients (Read-Only for unauthorized users)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        typer.echo("[bold red]Please login first: epic-events login[/bold red]")
        return
        
    get_all_clients(session, user)

@app.command()
def add_new_contract(
    client_id: int = typer.Option(..., prompt=True),
    total_amount: float = typer.Option(..., prompt=True),
    amount_due: float = typer.Option(..., prompt=True),
    signed: bool = typer.Option(False, prompt=True)
):
    """Add a new contract (Requires Admin or Commercial role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        typer.echo("[bold red]Please login first: epic-events login[/bold red]")
        return
        
    add_contract(session, user, client_id, total_amount, amount_due, signed)

@app.command()
def list_contracts():
    """List all contracts (Read-Only for all users)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        typer.echo("[bold red]Please login first: epic-events login[/bold red]")
        return
    
    get_all_contracts(session, user)

@app.command()
def add_new_event(
    contract_id: int = typer.Option(..., prompt=True),
    support_contact: str = typer.Option(..., prompt=True),
    start_date: str = typer.Option(..., prompt=True, help="Format: YYYY-MM-DD HH:MM"),
    end_date: str = typer.Option(..., prompt=True, help="Format: YYYY-MM-DD HH:MM"),
    location: str = typer.Option(..., prompt=True),
    attendees: int = typer.Option(..., prompt=True),
    notes: str = typer.Option("", prompt=True, help="Optional notes about the event")
):
    """Add a new event (Requires Admin, Support, or Gestion role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        typer.echo("[bold red]Please login first: epic-events login[/bold red]")
        return

    try:
        # Convert string dates to datetime objects
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        
        # If notes is empty string, set to None
        notes = notes if notes else None
        
        add_event(
            session=session,
            user=user,
            contract_id=contract_id,
            support_contact=support_contact,
            start_date=start_datetime,
            end_date=end_datetime,
            location=location,
            attendees=attendees,
            notes=notes
        )
    except ValueError as e:
        typer.echo("[bold red]Error: Invalid date format. Use YYYY-MM-DD[/bold red]")
    except Exception as e:
        typer.echo(f"[bold red]Error creating event: {str(e)}[/bold red]")

@app.command()
def list_events():
    """List all events (Read-Only for all users)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        typer.echo("[bold red]Please login first: epic-events login[/bold red]")
        return
    
    get_all_events(session, user)

if __name__ == "__main__":
    app()
