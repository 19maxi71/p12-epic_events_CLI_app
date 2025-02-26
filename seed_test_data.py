from datetime import datetime
import random
from epic_events.config import SessionLocal
from epic_events.crud import (
    add_client, get_db_session, authenticate_user,
    add_contract, add_event
)

def seed_test_data():
    """Seed the database with test data."""
    session = get_db_session(SessionLocal)
    
    try:
        # Login as admin
        user = authenticate_user(session, "admin@email.com", "securepassword")
        if not user:
            print("[bold red]Error: Please run init_db.py first to create admin user[/bold red]")
            return

        # Add test client
        add_client(
            session=session,
            user=user,
            full_name="Test Client",
            email="test@client.com",
            phone="+33612345678",
            company_name="Test Company Inc."
        )

        # Add test contract
        add_contract(
            session=session,
            user=user,
            client_id=1,
            total_amount=5000.0,
            amount_due=2500.0,
            signed=True
        )

        # Add test event
        add_event(
            session=session,
            user=user,
            contract_id=1,
            support_contact="Test Support",
            start_date=datetime.strptime("2025-06-10 14:00", "%Y-%m-%d %H:%M"),
            end_date=datetime.strptime("2025-06-10 22:00", "%Y-%m-%d %H:%M"),
            location="Test Location",
            attendees=50,
            notes="Test Event"
        )

        print("[bold green]Test data seeded successfully![/bold green]")

    except Exception as e:
        print(f"[bold red]Error seeding test data: {str(e)}[/bold red]")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_test_data()