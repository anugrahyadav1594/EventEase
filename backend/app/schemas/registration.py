"""Registration request / response schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .common import AttendanceStatus, ORMModel, RegistrationStatus


class RegistrationCreate(BaseModel):
    attendee_id: int = Field(..., gt=0)
    event_id: int = Field(..., gt=0)
    ticket_type: str | None = Field(default=None, max_length=40)
    ticket_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    registration_status: RegistrationStatus = RegistrationStatus.Registered
    registration_date: datetime | None = None


class RegistrationStatusUpdate(BaseModel):
    registration_status: RegistrationStatus
    note: str | None = Field(default=None, max_length=300)


class AttendanceUpdate(BaseModel):
    attendance_status: AttendanceStatus
    note: str | None = Field(default=None, max_length=300)


class RegistrationRead(ORMModel):
    registration_id: int
    attendee_id: int
    attendee_name: str | None = None
    attendee_email: str | None = None
    event_id: int
    event_name: str | None = None
    event_category: str | None = None
    event_date: str | None = None
    venue_name: str | None = None
    registration_date: datetime | None = None
    registration_status: str
    attendance_status: str
    ticket_type: str | None = None
    ticket_price: Decimal = Decimal("0")
    payment_status: str | None = None
    amount_paid: Decimal = Decimal("0")
