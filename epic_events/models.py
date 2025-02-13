from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .config import Base

class Client(Base):
    __tablename__ = "clients" # table name in db

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Client {self.full_name} ({self.company_name})>"


class Contract(Base):
    __tablename__ = "contracts" # table name in db

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    sales_contact = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    signed = Column(Boolean, default=False)

    client = relationship("Client", back_populates="contracts")

    def __repr__(self):
        return f"<Contract {self.id} | Client {self.client_id} | Signed: {self.signed}>"

# Add this to the Client model to establish the relationship
Client.contracts = relationship("Contract", back_populates="client", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    support_contact = Column(String, nullable=True)  # Assigned support staff
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
