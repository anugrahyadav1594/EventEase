"""Attendee request / response schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from .common import ORMModel


class AttendeeBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=140)
    email: EmailStr = Field(..., max_length=160)
    phone: str | None = Field(default=None, max_length=25)
    organization: str | None = Field(default=None, max_length=160)


class AttendeeCreate(AttendeeBase):
    pass


class AttendeeUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=140)
    email: EmailStr | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=25)
    organization: str | None = Field(default=None, max_length=160)


class AttendeeRead(ORMModel):
    attendee_id: int
    full_name: str
    email: str
    phone: str | None = None
    organization: str | None = None
    registration_date: datetime | None = None
    total_registrations: int = 0
    events_attended: int = 0
    total_paid: Decimal = Decimal("0")
