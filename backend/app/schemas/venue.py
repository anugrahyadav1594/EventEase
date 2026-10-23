"""Venue request / response schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field

from .common import ORMModel, VenueAvailability


class VenueBase(BaseModel):
    venue_name: str = Field(..., min_length=2, max_length=120)
    location: str = Field(..., min_length=2, max_length=200)
    capacity: int = Field(..., gt=0, le=1_000_000)
    venue_type: str | None = Field(default=None, max_length=60)
    availability_status: VenueAvailability = VenueAvailability.Available


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    venue_name: str | None = Field(default=None, min_length=2, max_length=120)
    location: str | None = Field(default=None, min_length=2, max_length=200)
    capacity: int | None = Field(default=None, gt=0, le=1_000_000)
    venue_type: str | None = Field(default=None, max_length=60)
    availability_status: VenueAvailability | None = None


class VenueRead(ORMModel):
    venue_id: int
    venue_name: str
    location: str
    capacity: int
    venue_type: str | None = None
    availability_status: str
    events_hosted: int = 0
    total_registrations: int = 0
    utilization_percent: float = 0.0
