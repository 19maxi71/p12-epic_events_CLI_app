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
        print("[bold yellow]No contracts found.[/bold yellow]")
        return
    
    table_of_contracts = Table(
        title="[bold bright_blue]Epic Events Contracts[/bold bright_blue]",
        title_style="white on blue",
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

