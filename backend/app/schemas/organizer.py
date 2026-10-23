"""Organizer request / response schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .common import ORMModel


class OrganizerBase(BaseModel):
    organizer_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr = Field(..., max_length=160)
    phone: str | None = Field(default=None, max_length=25)
    organization_name: str | None = Field(default=None, max_length=160)


class OrganizerCreate(OrganizerBase):
    pass


class OrganizerUpdate(BaseModel):
    organizer_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=25)
    organization_name: str | None = Field(default=None, max_length=160)


class OrganizerRead(ORMModel):
    model_config = ConfigDict(from_attributes=True)

    organizer_id: int
    organizer_name: str
    email: str
    phone: str | None = None
    organization_name: str | None = None
    created_at: datetime | None = None
    events_managed: int = 0
    total_registrations: int = 0
