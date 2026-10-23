"""Attendee CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..models import attendees, payments, registrations
from ..schemas import AttendeeCreate, AttendeeRead, AttendeeUpdate
from ..services.helpers import apply_pagination, integrity_error, jsonable_rows, rows_as_dicts

router = APIRouter(prefix="/attendees", tags=["attendees"])

# Correlated sub queries keep the counters correct (a join with payments would
# otherwise multiply the registration rows).
_registrations_count = (
    select(func.count())
    .select_from(registrations)
    .where(registrations.c.attendee_id == attendees.c.attendee_id)
    .scalar_subquery()
)
_attended_count = (
    select(func.count())
    .select_from(registrations)
    .where(
        registrations.c.attendee_id == attendees.c.attendee_id,
        registrations.c.attendance_status == "Present",
    )
    .scalar_subquery()
)
_total_paid = (
    select(func.coalesce(func.sum(payments.c.amount), 0))
    .select_from(
        registrations.join(payments, payments.c.registration_id == registrations.c.registration_id)
    )
    .where(
        registrations.c.attendee_id == attendees.c.attendee_id,
        payments.c.payment_status == "Completed",
    )
    .scalar_subquery()
)

ATTENDEE_LIST_QUERY = select(
    attendees,
    _registrations_count.label("total_registrations"),
    _attended_count.label("events_attended"),
    _total_paid.label("total_paid"),
).order_by(attendees.c.full_name)


@router.get("")
def list_attendees(
    session: Session = Depends(get_db),
    search: str | None = Query(default=None, description="Search by name, e-mail or organisation"),
    organization: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    statement = ATTENDEE_LIST_QUERY
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            attendees.c.full_name.ilike(pattern)
            | attendees.c.email.ilike(pattern)
            | attendees.c.organization.ilike(pattern)
        )
    if organization:
        statement = statement.where(attendees.c.organization == organization)
    return apply_pagination(statement, session, page, page_size)


@router.get("/{attendee_id}", response_model=AttendeeRead)
def get_attendee(attendee_id: int, session: Session = Depends(get_db)):
    row = session.execute(ATTENDEE_LIST_QUERY.where(attendees.c.attendee_id == attendee_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attendee {attendee_id} was not found.")
    return jsonable_rows(rows_as_dicts([row]))[0]


@router.get("/{attendee_id}/registrations")
def attendee_registrations(attendee_id: int, session: Session = Depends(get_db)):
    """Registration history of a single attendee."""
    rows = session.execute(
        select(
            registrations,
            func.count(payments.c.payment_id).label("payment_count"),
        )
        .select_from(registrations.outerjoin(payments, payments.c.registration_id == registrations.c.registration_id))
        .where(registrations.c.attendee_id == attendee_id)
        .group_by(registrations.c.registration_id)
        .order_by(registrations.c.registration_date.desc())
    ).all()
    return jsonable_rows(rows_as_dicts(rows))


@router.post("", response_model=AttendeeRead, status_code=status.HTTP_201_CREATED)
def create_attendee(payload: AttendeeCreate, session: Session = Depends(get_db)):
    try:
        result = session.execute(attendees.insert().values(**payload.model_dump()))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="attendee")
    return get_attendee(int(result.inserted_primary_key[0]), session)


@router.put("/{attendee_id}", response_model=AttendeeRead)
def update_attendee(attendee_id: int, payload: AttendeeUpdate, session: Session = Depends(get_db)):
    existing = session.execute(select(attendees.c.attendee_id).where(attendees.c.attendee_id == attendee_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attendee {attendee_id} was not found.")
    values = payload.model_dump(exclude_none=True)
    if values:
        try:
            session.execute(attendees.update().where(attendees.c.attendee_id == attendee_id).values(**values))
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise integrity_error(exc, entity="attendee")
    return get_attendee(attendee_id, session)


@router.delete("/{attendee_id}")
def delete_attendee(attendee_id: int, session: Session = Depends(get_db)):
    existing = session.execute(select(attendees.c.attendee_id).where(attendees.c.attendee_id == attendee_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attendee {attendee_id} was not found.")
    try:
        session.execute(attendees.delete().where(attendees.c.attendee_id == attendee_id))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="attendee")
    return {"message": f"Attendee {attendee_id} was deleted."}
