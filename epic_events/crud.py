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
    # for client in clients:
    #     print(f"[bold bright_blue]{client.id}: {client.full_name} - {client.email} - {client.phone}[/bold bright_blue]")