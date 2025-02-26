from epic_events.config import engine, Base, SessionLocal
from epic_events.models import Role, User
from epic_events.crud import create_user, get_db_session

def init_database():
    """Initialize database with tables and required initial data."""
    # Create all tables
    Base.metadata.create_all(engine)
    print("[bold green]Database tables created successfully![/bold green]")

    # Initialize session
    session = get_db_session(SessionLocal)

    try:
        # Create roles if they don't exist
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

        # Create admin user if doesn't exist
        admin = session.query(User).filter_by(email="admin@email.com").first()
        if not admin:
            create_user(session, "John Admin", "admin@email.com", "securepassword", role_id=1)
            print("[bold green]Admin user created successfully![/bold green]")

    except Exception as e:
        print(f"[bold red]Error during initialization: {str(e)}[/bold red]")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")