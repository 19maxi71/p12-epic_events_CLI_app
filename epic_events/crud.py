from rich import print
from rich.console import Console
from rich.table import Table
import sys
import os
import sentry_sdk

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from sqlalchemy.orm import Session, object_session
from epic_events.models import Client, Contract, Event, Role, User
from datetime import datetime, timezone

def get_db_session(SessionLocal):
    """Create a new database session."""
    return SessionLocal()


def add_client(session: Session, user: User, full_name: str, email: str, phone: str, company_name: str):
    """Add a new client to the database with role-based access control."""
    
    if user.role_id not in [1, 2]:  # Only Admin and Commercial can create clients
        print("[bold red]Error: You do not have permission to add clients.[/bold red]")
        return

    new_client = Client(
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
        sales_contact_id=user.id
    )
    session.add(new_client)
    session.commit()
    print(f"[bold green]Client '{full_name}' added successfully![/bold green]")


def update_client(session: Session, user: User, client_id: int, full_name: str, email: str, phone: str, company_name: str):
    """Update client details with role-based access control."""
    
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        print("[bold red]Error: Client not found.[/bold red]")
        return
    
    # Permission check
    if user.role_id not in [1, 2]:  # Only Admin and Commercial can update
        print("[bold red]Error: You do not have permission to update clients.[/bold red]")
        return

    try:
        client.full_name = full_name
        client.email = email
        client.phone = phone
        client.company_name = company_name
        client.updated_at = datetime.now(timezone.utc)
        
        session.commit()
        print(f"[bold green]Client '{client.full_name}' updated successfully![/bold green]")
    except Exception as e:
        session.rollback()
        print(f"[bold red]Error updating client: {str(e)}[/bold red]")

def delete_client(session: Session, user: User, client_id: int):
    """Delete a client with role-based access control."""
    
    if user.role_id != 1:  # Only Admin can delete clients
        print("[bold red]Error: You do not have permission to delete clients.[/bold red]")
        return

    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        print("[bold red]Error: Client not found.[/bold red]")
        return

    session.delete(client)
    session.commit()
    print(f"[bold green]Client '{client.full_name}' deleted successfully![/bold green]")

def get_all_clients(session: Session, user: User):
    """GET all clients from the database. 
    Everyone can read, but only authorized roles can edit."""
    with sentry_sdk.start_span(op="db", description="fetch_all_clients"):
        clients = session.query(Client).all()
    
    
    table_of_clients = Table(
        title=f"[bold bright_blue]Epic Events Clients[/bold bright_blue]",
        title_style="white on blue",
        title_justify="center",
        show_header=True,
        header_style="bold bright_white",
        border_style="blue"
    )
    
    table_of_clients.add_column("ID", justify="right", style="cyan")
    table_of_clients.add_column("Full Name", style="magenta")
    table_of_clients.add_column("Email", style="green")
    table_of_clients.add_column("Phone", style="yellow")
    table_of_clients.add_column("Company", style="blue")  # Fixed: Added as column
    
    for client in clients:
        table_of_clients.add_row(
            str(client.id), 
            client.full_name, 
            client.email, 
            client.phone,
            client.company_name  # Added company_name to the row
        )
    
    console = Console()
    console.print(table_of_clients)

    if user.role_id in [1, 2]:  # Admin or Commercial can modify
        print("[bold green]You have permission to edit clients.[/bold green]")
    else:
        print("[bold red]Read-only access: You cannot modify clients.[/bold red]")


def add_contract(session: Session, user: User, client_id: int, total_amount: float, amount_due: float, signed: bool = False):
    """Add a new contract to the database with role-based access control."""
    
    # 1. Permission check
    if user.role_id not in [1, 2]:  # Only Admin and Commercial can create contracts
        print("[bold red]Error: You do not have permission to add contracts.[/bold red]")
        return

    # 2. Client existence check
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        print("[bold red]Error: Client ID does not exist.[/bold red]")
        return

    # 3. Contract creation with proper association
    new_contract = Contract(
        client_id=client_id,
        sales_contact_id=user.id,  # Assign to the logged-in user
        total_amount=total_amount,
        amount_due=amount_due,
        signed=signed
    )
    session.add(new_contract)
    session.commit()
    print(f"[bold green]Contract for Client ID {client_id} added successfully![/bold green]")


def get_all_contracts(session: Session, user: User):
    """Retrieve all contracts from the database. Everyone can read, but only authorized roles can edit."""
    contracts = session.query(Contract).all()
    if not contracts:
        print("[bold red]No contracts found.[/bold red]")
        return
    
    table_of_contracts = Table(
        title="[bold magenta]Epic Events Contracts[/bold magenta]",
        title_style="white on orange_red1",
        title_justify="center",
        show_header=True,
        header_style="bold bright_white",
        border_style="blue"
    )
    
    table_of_contracts.add_column("ID", justify="right", style="cyan")
    table_of_contracts.add_column("Client ID", style="magenta")
    table_of_contracts.add_column("Total Amount", style="green")
    table_of_contracts.add_column("Amount Due", style="yellow")
    table_of_contracts.add_column("Status", style="cyan")
    
    for contract in contracts:
        status = "[green]Signed[/green]" if contract.signed else "[red]Not Signed[/red]"
        table_of_contracts.add_row(str(contract.id), str(contract.client_id), str(contract.total_amount), str(contract.amount_due), status)
    
    console = Console()
    console.print(table_of_contracts)

    if user.role_id in [1, 2]:  # Admin or Commercial can modify
        print("[bold green]You have permission to edit contracts.[/bold green]")
    else:
        print("[bold red]Read-only access: You cannot modify contracts.[/bold red]")
        

def add_event(session: Session, user: User, contract_id: int, support_contact: str, 
              start_date: datetime, end_date: datetime, location: str, 
              attendees: int, notes: str = None):
    """Add a new event to the database with role-based access control."""
    
    # 1. Permission check
    if user.role_id not in [1, 3, 4]:  # Only Admin, Support, and Gestion can create events
        print("[bold red]Error: You do not have permission to add events.[/bold red]")
        return

    # 2. Contract validation
    contract = session.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        print("[bold red]Error: Contract ID does not exist.[/bold red]")
        return
    if not contract.signed:
        print("[bold red]Error: Contract is not signed yet! Cannot create an event.[/bold red]")
        return

    # 3. Date validation
    if start_date >= end_date:
        print("[bold red]Error: Start date must be before end date.[/bold red]")
        return

    # 4. Event creation
    new_event = Event(
        contract_id=contract_id,
        support_contact=support_contact,
        start_date=start_date,
        end_date=end_date,
        location=location,
        attendees=attendees,
        notes=notes
    )
    
    try:
        session.add(new_event)
        session.commit()
        print(f"[bold green]Event for Contract ID {contract_id} added successfully![/bold green]")
    except Exception as e:
        session.rollback()
        print(f"[bold red]Error creating event: {str(e)}[/bold red]")

    
def get_all_events(session: Session, user: User):
    """Retrieve all events from the database. Everyone can read, but only authorized roles can edit."""
    events = session.query(Event).all()
    if not events:
        print("[bold yellow]No events found.[/bold yellow]")
        return

    table_of_events = Table(
        title="[bold blue]Epic Events[/bold blue]",
        title_style="white on bright_white",
        title_justify="center",
        show_header=True,
        header_style="bold bright_white",
        border_style="blue"
    )
    
    table_of_events.add_column("ID", justify="right", style="cyan")
    table_of_events.add_column("Contract ID", style="magenta")
    table_of_events.add_column("Location", style="green")
    table_of_events.add_column("Attendees", style="yellow")
    table_of_events.add_column("Start Date", style="cyan")
    table_of_events.add_column("End Date", style="magenta")
    table_of_events.add_column("Notes", style="green")
    
    for event in events:
        table_of_events.add_row(str(event.id), str(event.contract_id), event.location, str(event.attendees), str(event.start_date), str(event.end_date), event.notes)
    
    console = Console()
    console.print(table_of_events)

    if user.role_id in [1, 3, 4]:  # Admin, Support, or Gestion can modify
        print("[bold green]You have permission to edit events.[/bold green]")
    else:
        print("[bold red]Read-only access: You cannot modify events.[/bold red]")

def create_user(session: Session, full_name: str, email: str, password: str, role_id: int):
    """Create a new user with a hashed password."""
    try:
        # Check if role exists
        role = session.query(Role).filter(Role.id == role_id).first()
        if not role:
            print("[bold red]Error: Invalid role ID.[/bold red]")
            return

        new_user = User(full_name=full_name, email=email, role_id=role_id)
        new_user.set_password(password)  # Hash the password before saving
        session.add(new_user)
        session.commit()
        
        # Log successful user creation
        sentry_sdk.capture_message(
            f"New user created: {full_name}",
            level="info"
        )
        print(f"[bold green]User '{full_name}' created successfully![/bold green]")
    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        raise


def authenticate_user(session: Session, email: str, password: str):
    """Authenticate a user and log failed attempts to Sentry."""
    user = session.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        print(f"[bold green]Welcome, {user.full_name}![/bold green] (Role: {user.role.name})")
        return user
    else:
        sentry_sdk.capture_message(f"Failed login attempt for {email}", level="warning")
        print("[bold red]Error: Invalid email or password![/bold red]")
        return None

def update_contract(session: Session, user: User, contract_id: int, total_amount: float, amount_due: float, signed: bool):
    """Update contract details with role-based access control."""
    try:
        contract = session.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            print("[bold red]Error: Contract not found.[/bold red]")
            return

        # Only Admin, Gestion, or the assigned Commercial can update contracts
        if user.role_id not in [1, 2, 4] or (user.role_id == 2 and contract.sales_contact_id != user.id):
            print("[bold red]Error: You do not have permission to update this contract.[/bold red]")
            return

        contract.total_amount = total_amount
        contract.amount_due = amount_due
        contract.signed = signed
        contract.updated_at = datetime.now(timezone.utc)
        
        if signed and not contract.signed:  # Contract is being signed
            sentry_sdk.capture_message(
                f"Contract #{contract_id} signed",
                level="info",
                extras={
                    'client_id': contract.client_id,
                    'signed_by': user.full_name,
                }
            )
        session.commit()
        print(f"[bold green]Contract #{contract_id} updated successfully![/bold green]")
    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        raise

def update_event(session: Session, user: User, event_id: int, support_contact: str = None, start_date: datetime = None, end_date: datetime = None, location: str = None, attendees: int = None, notes: str = None):
    """Update event details with role-based access control."""
    
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        print("[bold red]Error: Event not found.[/bold red]")
        return

    # Only Admin or assigned Support can update
    if user.role_id not in [1, 3] or (user.role_id == 3 and event.support_contact != user.full_name):
        print("[bold red]Error: You do not have permission to update this event.[/bold red]")
        return

    # Update only provided fields
    if support_contact:
        event.support_contact = support_contact
    if start_date:
        event.start_date = start_date
    if end_date:
        event.end_date = end_date
    if location:
        event.location = location
    if attendees is not None:
        event.attendees = attendees
    if notes is not None:
        event.notes = notes

    session.commit()
    print(f"[bold green]Event {event.id} updated successfully![/bold green]")

def filter_events(user: User, session: Session,
                 event_id: int = None,
                 contract_id: int = None,
                 support_contact: str = None,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 location: str = None,
                 attendees: int = None):
    """Filter events by any criteria with role-based access."""
    try:
        # Start with base query
        query = session.query(Event)

        # Apply filters based on provided parameters
        if event_id:
            query = query.filter(Event.id == event_id)
        if contract_id:
            query = query.filter(Event.contract_id == contract_id)
        if support_contact:
            query = query.filter(Event.support_contact == support_contact)
        if start_date:
            query = query.filter(Event.start_date >= start_date)
        if end_date:
            query = query.filter(Event.end_date <= end_date)
        if location:
            query = query.filter(Event.location.ilike(f"%{location}%"))
        if attendees:
            query = query.filter(Event.attendees == attendees)

        # Role-based filtering
        if user.role_id == 3:  # Support
            query = query.filter(Event.support_contact == user.full_name)
        elif user.role_id == 4:  # Gestion
            query = query.filter(Event.support_contact == None)

        events = query.all()
        if not events:
            print("[bold yellow]No events found with these criteria.[/bold yellow]")
            return

        _display_events_table(events)

    except Exception as e:
        print(f"[bold red]Error filtering events: {str(e)}[/bold red]")

def filter_events_by_role(session: Session, user: User, **filters):
    """Filter events by any criteria with role-based access."""
    try:
        # Start with base query
        query = session.query(Event)

        # Apply filters based on provided parameters
        if filters.get('event_id'):
            query = query.filter(Event.id == filters['event_id'])
        if filters.get('contract_id'):
            query = query.filter(Event.contract_id == filters['contract_id'])
        if filters.get('support_contact'):
            query = query.filter(Event.support_contact == filters['support_contact'])
        if filters.get('start_date'):
            query = query.filter(Event.start_date >= filters['start_date'])
        if filters.get('end_date'):
            query = query.filter(Event.end_date <= filters['end_date'])
        if filters.get('location'):
            query = query.filter(Event.location.ilike(f"%{filters['location']}%"))
        if filters.get('attendees'):
            query = query.filter(Event.attendees == filters['attendees'])

        # Add role-based filtering
        if user.role_id == 3:  # Support
            query = query.filter(Event.support_contact == user.full_name)
        elif user.role_id == 4:  # Gestion
            query = query.filter(Event.support_contact == None)

        events = query.all()
        if not events:
            print("[bold yellow]No events found with these criteria.[/bold yellow]")
            return

        _display_events_table(events)

    except Exception as e:
        print(f"[bold red]Error filtering events: {str(e)}[/bold red]")

def filter_contracts_by_role(session: Session, user: User):
    """Filter contracts based on user role."""
    
    try:
        if user.role_id == 1:  # Admin
            print("[bold green]As Admin, you can see all event filters:[/bold green]")
            # Show both unassigned and all events
            unassigned_events = session.query(Event).filter(
                Event.support_contact == None
            ).all()
            all_events = session.query(Event).all()
            
            if unassigned_events:
                print("\n[bold yellow]Unassigned events:[/bold yellow]")
                _display_events_table(unassigned_events)
            
            print("\n[bold yellow]All events:[/bold yellow]")
            _display_events_table(all_events)
            
        elif user.role_id == 3:  # Support
            events = session.query(Event).filter(
                Event.support_contact == user.full_name
            ).all()
            if not events:
                print("[bold yellow]No events assigned to you.[/bold yellow]")
                return
                
            print(f"[bold green]Events assigned to {user.full_name}:[/bold green]")
            _display_events_table(events)
            
        elif user.role_id == 4:  # Gestion
            events = session.query(Event).filter(
                Event.support_contact == None
            ).all()
            if not events:
                print("[bold yellow]No unassigned events found.[/bold yellow]")
                return
                
            print("[bold green]Unassigned events:[/bold green]")
            _display_events_table(events)
            
        else:
            print("[bold red]Error: Your role cannot filter events.[/bold red]")
            
    except Exception as e:
        print(f"[bold red]Error filtering events: {str(e)}[/bold red]")

def _display_events_table(events):
    """Helper function to display events in a table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Contract")
    table.add_column("Support Contact")
    table.add_column("Start Date")
    table.add_column("Location")
    table.add_column("Attendees")
    
    for event in events:
        table.add_row(
            str(event.id),
            str(event.contract_id),
            event.support_contact or "Unassigned",
            event.start_date.strftime("%Y-%m-%d"),
            event.location,
            str(event.attendees)
        )
    
    console = Console()
    console.print(table)

def filter_contracts_by_role(session: Session, user: User):
    """Filter contracts based on user role."""
    try:
        if user.role_id == 1:  # Admin
            print("[bold green]As Admin, you can see all contract filters:[/bold green]")
            # Show both unsigned and all contracts
            unsigned_contracts = session.query(Contract).filter(
                Contract.signed == False
            ).all()
            all_contracts = session.query(Contract).all()
            
            if unsigned_contracts:
                print("\n[bold yellow]Unsigned contracts:[/bold yellow]")
                _display_contracts_table(unsigned_contracts)
            
            print("\n[bold yellow]All contracts:[/bold yellow]")
            _display_contracts_table(all_contracts)
            
        elif user.role_id == 2:  # Commercial
            contracts = session.query(Contract).filter(
                Contract.signed == False,
                Contract.sales_contact_id == user.id
            ).all()
            
            if not contracts:
                print("[bold yellow]No unsigned contracts found.[/bold yellow]")
                return
                
            print("[bold green]Your unsigned contracts:[/bold green]")
            _display_contracts_table(contracts)
        else:
            print("[bold red]Error: Your role cannot filter contracts.[/bold red]")
            
    except Exception as e:
        print(f"[bold red]Error filtering contracts: {str(e)}[/bold red]")

def _display_contracts_table(contracts):
    """Helper function to display contracts in a table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Client ID")
    table.add_column("Total Amount")
    table.add_column("Amount Due")
    table.add_column("Status")
    
    for contract in contracts:
        status = "[green]Signed[/green]" if contract.signed else "[red]Not Signed[/red]"
        table.add_row(
            str(contract.id),
            str(contract.client_id),
            f"${contract.total_amount:,.2f}",
            f"${contract.amount_due:,.2f}",
            status
        )
    
    console = Console()
    console.print(table)

def filter_contracts(session: Session, user: User,
                    contract_id: int = None,
                    client_id: int = None,
                    total_amount_min: float = None,
                    total_amount_max: float = None,
                    signed: bool = None,
                    date_min: datetime = None,
                    date_max: datetime = None):
    """Filter contracts by any parameter."""
    try:
        # Start with base query
        query = session.query(Contract)

        # Apply filters based on provided parameters
        if contract_id:
            query = query.filter(Contract.id == contract_id)
        if client_id:
            query = query.filter(Contract.client_id == client_id)
        if total_amount_min:
            query = query.filter(Contract.total_amount >= total_amount_min)
        if total_amount_max:
            query = query.filter(Contract.total_amount <= total_amount_max)
        if signed is not None:
            query = query.filter(Contract.signed == signed)
        if date_min:
            query = query.filter(Contract.created_at >= date_min)
        if date_max:
            query = query.filter(Contract.created_at <= date_max)

        # Role-based filtering
        if user.role_id == 2:  # Commercial
            query = query.filter(Contract.sales_contact_id == user.id)
        elif user.role_id != 1:  # Not Admin
            print("[bold red]Error: Your role cannot filter contracts.[/bold red]")
            return

        contracts = query.all()
        if not contracts:
            print("[bold yellow]No contracts found with these criteria.[/bold yellow]")
            return

        _display_contracts_table(contracts)

    except Exception as e:
        print(f"[bold red]Error filtering contracts: {str(e)}[/bold red]")

def update_user_details(session: Session, user: User, target_email: str, **updates):
    """Update user details (Admin only)."""
    try:
        # Check if user is admin
        if user.role_id != 1:
            print("[bold red]Error: Only Admin can modify user details.[/bold red]")
            return

        # Find target user
        target_user = session.query(User).filter(User.email == target_email).first()
        if not target_user:
            print("[bold red]Error: User not found.[/bold red]")
            return

        # Update fields
        if 'full_name' in updates:
            target_user.full_name = updates['full_name']
        if 'email' in updates:
            target_user.email = updates['email']
        if 'password' in updates:
            target_user.set_password(updates['password'])

        session.commit()

        # Log to Sentry
        sentry_sdk.capture_message(
            f"User updated: {target_user.full_name}",
            level="info"
        )
        
        print(f"[bold green]User details updated successfully![/bold green]")
        
    except Exception as e:
        session.rollback()
        sentry_sdk.capture_exception(e)
        raise
