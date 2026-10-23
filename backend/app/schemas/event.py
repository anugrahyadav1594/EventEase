"""Event request / response schemas."""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from .common import ORMModel, EventStatus


class EventBase(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    event_category: str = Field(..., min_length=2, max_length=60)
    organizer_id: int = Field(..., gt=0)
    venue_id: int = Field(..., gt=0)
    event_date: date
    start_time: time
    end_time: time
    capacity: int = Field(..., gt=0, le=1_000_000)
    ticket_price: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    event_status: EventStatus = EventStatus.Upcoming

    @model_validator(mode="after")
    def _validate_times(self) -> "EventBase":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        if self.event_date.year < 2000:
            raise ValueError("event_date is not a valid date for an event")
        if self.event_date.year > date.today().year + 3:
            raise ValueError("event_date cannot be more than 3 years in the future")
        return self


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    event_name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    event_category: str | None = Field(default=None, min_length=2, max_length=60)
    organizer_id: int | None = Field(default=None, gt=0)
    venue_id: int | None = Field(default=None, gt=0)
    event_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    capacity: int | None = Field(default=None, gt=0, le=1_000_000)
    ticket_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    event_status: EventStatus | None = None

    @model_validator(mode="after")
    def _validate_times(self) -> "EventUpdate":
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        if self.event_date and self.event_date.year < 2000:
            raise ValueError("event_date is not a valid date for an event")
        return self


class EventRead(ORMModel):
    event_id: int
    event_name: str
    description: str | None = None
    event_category: str
    organizer_id: int
    organizer_name: str | None = None
    organization_name: str | None = None
    venue_id: int
    venue_name: str | None = None
    venue_location: str | None = None
    event_date: date
    start_time: time
    end_time: time
    capacity: int
    ticket_price: Decimal
    event_status: str
    created_at: datetime | None = None
    registration_count: int = 0
    confirmed_count: int = 0
    present_count: int = 0
    seats_available: int = 0
    fill_rate_percent: float = 0.0
    revenue: Decimal = Decimal("0")
