from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Event(Base):
    __tablename__ = "events"

    # Primary Key
    event_id = Column(Integer, name="event_id", primary_key=True, autoincrement=True, index=True)

    # Other Columns
    event_name = Column(String, name="event_name", nullable=False, unique=True, index=True)
    total_seats = Column(Integer, name="total_seats", nullable=False)
    available_seats = Column(Integer, name="available_seats", nullable=False)
    event_date = Column(DateTime, name="event_date", nullable=False)

    registrations = relationship("Registration", back_populates="event")

class Registration(Base):
    __tablename__ = "registrations"

    # Primary Key
    reg_id = Column(Integer, name="reg_id", primary_key=True, autoincrement=True, index=True)

    # Other Columns
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)
    user_name = Column(String, name="user_name", nullable=False, index=True)
    timestamp = Column(DateTime, name="timestamp", default=datetime.utcnow)

    event = relationship("Event", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint('user_name', 'event_id', name='uq_user_event_registration'),
    )

