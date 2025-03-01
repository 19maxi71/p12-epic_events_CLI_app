import typer
from rich import print
from rich.console import Console
from epic_events.config import SessionLocal
from epic_events.crud import (
    add_client, get_all_clients, add_contract, get_all_contracts, 
    add_event, get_all_events, create_user, authenticate_user,
    update_client as crud_update_client,
    update_contract as crud_update_contract,
    update_event as crud_update_event,
    filter_events_by_role,
    filter_contracts_by_role,
    update_user_details 
)
from epic_events.auth import ( 
    get_current_user, clear_current_user, 
    create_token, save_token
)
from datetime import datetime
import sentry_sdk


console = Console() 

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
        print(f"[bold green]Logged in as: {user.full_name} (Role: {user.role.name})[/bold green]")
    else:
        print("[bold red]Login failed.[/bold red]")

@app.command()
def logout():
    """Logout current user"""
    clear_current_user()
    print("[bold green]Logged out successfully![/bold green]")

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
        print("[bold red]Please login first: epic-events login[/bold red]")
        return
        
    add_client(session, user, full_name, email, phone, company_name)

@app.command()
def list_clients():
    """List all clients (Read-Only for unauthorized users)."""
    with sentry_sdk.start_transaction(op="command", name="list_clients"):
        session = next(get_db())
        user = get_current_user(session)
        
        if not user:
            print("[bold red]Please login first: epic-events login[/bold red]")
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
        print("[bold red]Please login first: epic-events login[/bold red]")
        return
        
    add_contract(session, user, client_id, total_amount, amount_due, signed)

@app.command()
def list_contracts():
    """List all contracts (Read-Only for all users)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return
    
    get_all_contracts(session, user)

@app.command()
def add_new_event(
    contract_id: int = typer.Option(..., prompt=True),
    support_contact: str = typer.Option(..., prompt=True),
    start_date: str = typer.Option(..., prompt=True, help="Format: DD/MM/YYYY HH:MM"),
    end_date: str = typer.Option(..., prompt=True, help="Format: DD/MM/YYYY HH:MM"),
    location: str = typer.Option(..., prompt=True),
    attendees: int = typer.Option(..., prompt=True),
    notes: str = typer.Option("", prompt=True, help="Optional notes about the event")
):
    """Add a new event (Requires Admin, Support, or Gestion role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    try:
        # Convert French format to datetime objects
        start_datetime = datetime.strptime(start_date, "%d/%m/%Y")
        end_datetime = datetime.strptime(end_date, "%d/%m/%Y")
        
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
        print("[bold red]Error: Invalid date format. Use DD/MM/YYYY[/bold red]")
    except Exception as e:
        print(f"[bold red]Error creating event: {str(e)}[/bold red]")

@app.command()
def list_events():
    """List all events (Read-Only for all users)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return
    
    get_all_events(session, user)
      
@app.command()
def update_client(
    client_id: int = typer.Option(..., prompt=True),
    full_name: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    phone: str = typer.Option(..., prompt=True),
    company_name: str = typer.Option(..., prompt=True)
):
    """Update an existing client (Requires Admin or Commercial role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    crud_update_client( 
        session=session,
        user=user,
        client_id=client_id,
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name
    )

@app.command()
def update_contract(
    contract_id: int = typer.Option(..., prompt=True),
    total_amount: float = typer.Option(..., prompt=True),
    amount_due: float = typer.Option(..., prompt=True),
    signed: bool = typer.Option(..., prompt=True)
):
    """Update contract details (Requires Admin, Gestion, or assigned Commercial role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    crud_update_contract(
        session=session,
        user=user,
        contract_id=contract_id,
        total_amount=total_amount,
        amount_due=amount_due,
        signed=signed
    )

@app.command()
def update_event(
    event_id: int = typer.Option(..., prompt=True),
    support_contact: str = typer.Option(None, prompt="New Support Contact (press Enter to skip)"),
    start_date: str = typer.Option(None, prompt="New Start Date (YYYY-MM-DD, press Enter to skip)"),
    end_date: str = typer.Option(None, prompt="New End Date (YYYY-MM-DD, press Enter to skip)"),
    location: str = typer.Option(None, prompt="New Location (press Enter to skip)"),
    attendees: int = typer.Option(None, prompt="New Number of Attendees (press Enter to skip)"),
    notes: str = typer.Option(None, prompt="New Notes (press Enter to skip)")
):
    """Update event details (Requires Admin or assigned Support role)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    try:
        # Convert dates if provided
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        # Convert empty strings to None
        support_contact = support_contact if support_contact and support_contact.strip() else None
        location = location if location and location.strip() else None
        notes = notes if notes and notes.strip() else None
        
        crud_update_event(
            session=session,
            user=user,
            event_id=event_id,
            support_contact=support_contact,
            start_date=start_datetime,
            end_date=end_datetime,
            location=location,
            attendees=attendees,
            notes=notes
        )
    except ValueError as e:
        print("[bold red]Error: Invalid date format. Use YYYY-MM-DD[/bold red]")
    except Exception as e:
        print(f"[bold red]Error updating event: {str(e)}[/bold red]")

@app.command()
def filter_events(
    event_id: int = typer.Option(None, "--id", help="Filter by event ID"),
    contract_id: int = typer.Option(None, "--contract", help="Filter by contract ID"),
    support_contact: str = typer.Option(None, "--support", help="Filter by support contact"),
    start_date: str = typer.Option(None, "--start", help="Filter by start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", help="Filter by end date (YYYY-MM-DD)"),
    location: str = typer.Option(None, "--location", help="Filter by location"),
    attendees: int = typer.Option(None, "--attendees", help="Filter by number of attendees")
):
    """Filter events by any criteria."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    # Convert dates if provided
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

    # Create filters dictionary with only non-None values
    filters = {
        'event_id': event_id,
        'contract_id': contract_id,
        'support_contact': support_contact,
        'start_date': start,
        'end_date': end,
        'location': location,
        'attendees': attendees
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    filter_events_by_role(session=session, user=user, **filters)

@app.command()
def filter_contracts():
    """Filter contracts based on role (Commercial → Unsigned contracts)."""
    session = next(get_db())
    user = get_current_user(session)

    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    filter_contracts_by_role(session, user)

@app.command()
def test_sentry():
    """Test Sentry error tracking by raising a test error."""
    try:
        print("[bold yellow]Testing Sentry integration [/bold yellow]")
        division_by_zero = 1 / 0
    except ZeroDivisionError as e:
        # Capture and send the error to Sentry
        sentry_sdk.capture_exception(e)
        print("[bold red]Test error generated and sent to Sentry![/bold red]")
        # Re-raise the error to show the traceback
        raise

@app.command()
def update_user(
    target_email: str = typer.Option(..., prompt=True),
    new_name: str = typer.Option(None, "--name", help="New full name"),
    new_email: str = typer.Option(None, "--email", help="New email address"),
    new_password: str = typer.Option(None, "--password", help="New password", hide_input=True)
):
    """Update user details (Admin only)."""
    session = next(get_db())
    user = get_current_user(session)
    
    if not user:
        print("[bold red]Please login first: epic-events login[/bold red]")
        return

    updates = {}
    if new_name:
        updates['full_name'] = new_name
    if new_email:
        updates['email'] = new_email
    if new_password:
        updates['password'] = new_password

    update_user_details(session, user, target_email, **updates)

if __name__ == "__main__":
    app()
