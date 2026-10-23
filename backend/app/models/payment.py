"""Payments table - ticket payments recorded for registrations.

Revenue is always derived from this table: only rows with
`payment_status = 'Completed'` count as collected money, and refunded rows are
never counted again (a refund flips the row to `Refunded`).
"""
from __future__ import annotations

from sqlalchemy import (
    text,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    text,
)

from .base import metadata
from .registration import registrations

payment_method_enum = Enum(
    "Cash",
    "UPI",
    "Card",
    "Bank Transfer",
    name="payment_method",
)

payment_status_enum = Enum(
    "Pending",
    "Completed",
    "Refunded",
    name="payment_status",
)

payments = Table(
    "payments",
    metadata,
    Column("payment_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "registration_id",
        Integer,
        ForeignKey("registrations.registration_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("amount", Numeric(10, 2), nullable=False),
    Column("payment_method", payment_method_enum, nullable=False),
    Column(
        "payment_status",
        payment_status_enum,
        nullable=False,
        server_default="Pending",
    ),
    Column("transaction_reference", String(120), unique=True),
    Column("payment_date", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    CheckConstraint("amount >= 0", name="ck_payments_amount_non_negative"),
    Index("ix_payments_registration_id", "registration_id"),
    Index("ix_payments_payment_status", "payment_status"),
)
