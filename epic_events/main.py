import sys
import os
from datetime import datetime
import random

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from epic_events.config import engine, Base, SessionLocal
from epic_events.models import Client, Contract, Event, Role, User
from epic_events.crud import (
    add_client, get_db_session, get_all_clients, 
    add_contract, get_all_contracts, add_event, 
    get_all_events, create_user, authenticate_user
)




def setup_database():
    """Creates the database and tables."""
    Base.metadata.create_all(engine)
    print("Database updated with Contracts and Events.")

def test_add_client():
    session = get_db_session(SessionLocal)
    add_client(session, "Botter USE", "botteruse.com", "0777777777", "botter use inc.")

def test_get_clients():
    session = get_db_session(SessionLocal)
    get_all_clients(session)

def test_add_contract():
    session = get_db_session(SessionLocal)
    add_contract(session, client_id=1, sales_contact="LIDL", total_amount=1000.0, amount_due=500.0, signed=True)

def test_get_contracts():
    session = get_db_session(SessionLocal)
    get_all_contracts(session)

def test_add_event():
    session = get_db_session(SessionLocal)
    add_event(
        session,
        contract_id=2,
        support_contact="Jean-Michel",
        start_date=datetime.strptime("2025-05-10 14:00", "%Y-%m-%d %H:%M"),
        end_date=datetime.strptime("2025-05-10 22:00", "%Y-%m-%d %H:%M"),
        location="Avranches",
        attendees=100,
        notes="Le resto de couer"
    )

def test_get_events():
    session = get_db_session(SessionLocal)
    get_all_events(session)

def test_user_creation():
    session = get_db_session(SessionLocal)

    # Check if roles already exist
    existing_roles = session.query(Role).count()
    if existing_roles == 0:
        session.add_all([
            Role(id=1, name="Admin"),
            Role(id=2, name="Commercial"),
            Role(id=3, name="Support"),
            Role(id=4, name="Gestion")
        ])
        session.commit()
        print("[bold green]Roles initialized successfully![/bold green]")
    else:
        print("[bold yellow]Roles already exist, skipping initialization.[/bold yellow]")

    # Create a test user (only if they don't exist)
    existing_user = session.query(User).filter_by(email="admin@email.com").first()
    if not existing_user:
        create_user(session, "John Admin", "admin@email.com", "securepassword", role_id=1)
    else:
        print("[bold yellow]User 'John Admin' already exists, skipping creation.[/bold yellow]")


def test_authentication():
    session = get_db_session(SessionLocal)
    authenticate_user(session, "admin@email.com", "securepassword")

def test_read_access():
    session = get_db_session(SessionLocal)

    # Authenticate as an example user
    user = authenticate_user(session, "admin@email.com", "securepassword")
    if user:
        get_all_clients(session, user)
        get_all_contracts(session, user)
        get_all_events(session, user)

def test_permissions():
    session = get_db_session(SessionLocal)

    # Authenticate as Admin
    user = authenticate_user(session, "admin@email.com", "securepassword")
    if user:
        try:
            # Add client
            add_client(
                session=session,
                user=user,
                full_name=f'BOT {datetime.now().timestamp()}',
                email=f"client_{datetime.now().timestamp()}@email.com",
                phone=f"+33+random.randint(100000000, 999999999)",
                company_name=f"Boite de test {datetime.now().timestamp()}"
            )

            # Add contract - Updated parameters
            add_contract(
                session=session,
                user=user,
                client_id=1,
                total_amount=random.randint(1000, 10000),
                amount_due=random.randint(500, 5000),
                signed=True
            )

            # Add event with proper datetime objects
            add_event(
                session=session,
                user=user,
                contract_id=1,
                support_contact="Mec du support",
                start_date=datetime.strptime("2025-06-10 14:00", "%Y-%m-%d %H:%M"),
                end_date=datetime.strptime("2025-06-11 14:00", "%Y-%m-%d %H:%M"),
                location="AVRANCHES",
                attendees=100,
                notes="RESTO DE COEUR"
            )
        except Exception as e:
            print(f"[bold red]Error during test: {str(e)}[/bold red]")
            session.rollback()

if __name__ == "__main__":
    setup_database()
    # test_add_client()
    # test_get_clients()
    # test_add_contract()
    # test_get_contracts()
    # test_add_event()
    # test_get_events()
    test_user_creation()
    # test_authentication()
    # test_read_access()
    test_permissions()