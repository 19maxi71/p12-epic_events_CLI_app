from rich import print
from rich.console import Console
from rich.table import Table
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
    print(f"[bold green]Client '{full_name}' added successfully![/bold green]")


def get_all_clients(session: Session):
    """Get all clients from the database."""
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
    
    for client in clients:
        table_of_clients.add_row(str(client.id), client.full_name, client.email, client.phone)
    console = Console()
    console.print(table_of_clients)

def add_contract(session: Session, client_id: int, sales_contact: str, total_amount: float, amount_due: float, signed: bool = False):
    """Add a new contract to the database."""
    
    # Check if the client exists
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        print("[bold red]Error: Client ID does not exist.[/bold red]")
        return

    new_contract = Contract(
        client_id=client_id,
        sales_contact=sales_contact,
        total_amount=total_amount,
        amount_due=amount_due,
        signed=signed
    )
    session.add(new_contract)
    session.commit()
    print(f"[bold green]Contract for Client ID {client_id} added successfully![/bold green]")

def get_all_contracts(session: Session):
    """Retrieve all contracts from the database."""
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

def add_event(session: Session, contract_id: int, support_contact: str, start_date: str, end_date: str, location: str, attendees: int, notes: str = None):
    """Add a new event to the database."""
    
    # Check if the contract exists and is signed
    contract = session.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        print("[bold red]Error: Contract ID does not exist.[/bold red]")
        return
    if not contract.signed:
        print("[bold red]Error: Contract is not signed yet! Cannot create an event.[/bold red]")
        return

    new_event = Event(
        contract_id=contract_id,
        support_contact=support_contact,
        start_date=start_date,
        end_date=end_date,
        location=location,
        attendees=attendees,
        notes=notes
    )
    session.add(new_event)
    session.commit()
    print(f"[bold green]Event for Contract ID {contract_id} added successfully![/bold green]")
    
def get_all_events(session: Session):
    """Retrieve all events from the database."""
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
