"""Shared enumerations and helpers for the API schemas."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base model for response schemas."""

    model_config = ConfigDict(from_attributes=True)


class EventStatus(str, Enum):
    Upcoming = "Upcoming"
    Ongoing = "Ongoing"
    Completed = "Completed"
    Cancelled = "Cancelled"


class VenueAvailability(str, Enum):
    Available = "Available"
    Unavailable = "Unavailable"
    Maintenance = "Maintenance"


class RegistrationStatus(str, Enum):
    Registered = "Registered"
    Confirmed = "Confirmed"
    Cancelled = "Cancelled"
    Waitlisted = "Waitlisted"


class AttendanceStatus(str, Enum):
    NotMarked = "Not Marked"
    Present = "Present"
    Absent = "Absent"


class PaymentMethod(str, Enum):
    Cash = "Cash"
    UPI = "UPI"
    Card = "Card"
    BankTransfer = "Bank Transfer"


class PaymentStatus(str, Enum):
    Pending = "Pending"
    Completed = "Completed"
    Refunded = "Refunded"


class Message(BaseModel):
    message: str
