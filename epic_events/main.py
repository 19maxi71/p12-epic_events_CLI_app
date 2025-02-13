import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from epic_events.config import engine, Base, SessionLocal
from epic_events.models import Client, Contract, Event
from epic_events.crud import add_client, get_db_session, get_all_clients, add_contract, get_all_contracts

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
    add_contract(session, client_id=1, sales_contact="VENDEUR MACHIN", total_amount=5000.0, amount_due=2500.0, signed=False)

def test_get_contracts():
    session = get_db_session(SessionLocal)
    get_all_contracts(session)


if __name__ == "__main__":
    # setup_database()
    # test_add_client()
    # test_get_clients()
    # test_add_contract()
    test_get_contracts()
