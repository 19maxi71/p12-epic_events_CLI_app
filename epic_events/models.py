from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .config import Base
from werkzeug.security import generate_password_hash, check_password_hash


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # "Admin", "Commercial", "Support", "Gestion"

    def __repr__(self):
        return f"<Role {self.id} | {self.name}>"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)  # Role reference
    password_hash = Column(String, nullable=False)  # Store hashed password

    role = relationship("Role")

    def set_password(self, password):
        """Hashes the password before storing it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the entered password is correct."""
        return check_password_hash(self.password_hash, password)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    sales_contact_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Link to User
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    sales_contact = relationship("User")  # Establish a relationship with User



class Contract(Base):
    __tablename__ = "contracts" # table name in db

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    sales_contact_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Changed from String
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    signed = Column(Boolean, default=False)

    client = relationship("Client", back_populates="contracts")
    sales_contact = relationship("User")  # Add relationship to User model

    def __repr__(self):
        return f"<Contract {self.id} | Client {self.client_id} | Signed: {self.signed}>"

# Add this to the Client model to establish the relationship
Client.contracts = relationship("Contract", back_populates="client", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    support_contact = Column(String, nullable=True)  # id of the support contact
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)

    contract = relationship("Contract", back_populates="events")

    def __repr__(self):
        return f"<Event {self.id} | Contract {self.contract_id} | Location: {self.location}>"

# Add this to the Contract model to establish the relationship
Contract.events = relationship("Event", back_populates="contract", cascade="all, delete-orphan")
