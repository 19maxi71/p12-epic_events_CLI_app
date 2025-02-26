from datetime import datetime, timedelta
from faker import Faker
import random
from epic_events.config import SessionLocal
from epic_events.crud import (
    add_client, get_db_session, authenticate_user,
    add_contract, add_event
)

fake = Faker(['fr_FR'])  # French locale

def generate_random_client():
    """Generate random client data"""
    return {
        'full_name': fake.name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'company_name': fake.company()
    }

def generate_random_contract():
    """Generate random contract data"""
    total = round(random.uniform(1000.0, 10000.0), 2)
    return {
        'total_amount': total,
        'amount_due': round(random.uniform(0, total), 2),
        'signed': random.choice([True, False])
    }

def generate_random_event():
    """Generate random event data"""
    start = fake.date_time_between(start_date='+1d', end_date='+1y')
    return {
        'support_contact': fake.name(),
        'start_date': start,
        'end_date': start + timedelta(hours=random.randint(2, 8)),
        'location': fake.city(),
        'attendees': random.randint(10, 200),
        'notes': fake.text(max_nb_chars=200)
    }

def seed_test_data(num_clients=5):
    """Seed the database with random test data."""
    session = get_db_session(SessionLocal)
    
    try:
        # Login as admin
        user = authenticate_user(session, "email", "password")  # Your current admin credentials
        if not user:
            print("[bold red]Error: Please run init_db.py first to create admin user[/bold red]")
            return

        # Add multiple test clients
        for _ in range(num_clients):
            client_data = generate_random_client()
            add_client(
                session=session,
                user=user,
                **client_data
            )
            
            # Add 1-3 contracts per client
            for _ in range(random.randint(1, 3)):
                contract_data = generate_random_contract()
                add_contract(
                    session=session,
                    user=user,
                    client_id=_ + 1,
                    **contract_data
                )
                
                # Add 1-5 events per contract
                for _ in range(random.randint(1, 5)):
                    event_data = generate_random_event()
                    add_event(
                        session=session,
                        user=user,
                        contract_id=_ + 1,
                        **event_data
                    )

        print("[bold green]Random test data seeded successfully![/bold green]")

    except Exception as e:
        print(f"[bold red]Error seeding test data: {str(e)}[/bold red]")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_test_data()