"""Payment request / response schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .common import ORMModel, PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    registration_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    payment_method: PaymentMethod
    payment_status: PaymentStatus = PaymentStatus.Pending
    transaction_reference: str | None = Field(default=None, max_length=120)
    payment_date: datetime | None = None


class PaymentStatusUpdate(BaseModel):
    payment_status: PaymentStatus
    note: str | None = Field(default=None, max_length=300)


class PaymentRead(ORMModel):
    payment_id: int
    registration_id: int
    attendee_id: int | None = None
    attendee_name: str | None = None
    event_id: int | None = None
    event_name: str | None = None
    amount: Decimal
    payment_method: str
    payment_status: str
    transaction_reference: str | None = None
    payment_date: datetime | None = None
