"""Venue CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..models import events, registrations, venues
from ..schemas import VenueCreate, VenueRead, VenueUpdate
from ..services.helpers import apply_pagination, integrity_error, jsonable_rows, rows_as_dicts

router = APIRouter(prefix="/venues", tags=["venues"])

# The counters are built with correlated sub queries so that joining events
# with registrations can never multiply the numbers.
_events_hosted = (
    select(func.count()).select_from(events).where(events.c.venue_id == venues.c.venue_id).scalar_subquery()
)
_registrations_count = (
    select(func.count())
    .select_from(registrations.join(events, events.c.event_id == registrations.c.event_id))
    .where(events.c.venue_id == venues.c.venue_id)
    .scalar_subquery()
)
_seats_offered = (
    select(func.coalesce(func.sum(events.c.capacity), 0))
    .select_from(events)
    .where(events.c.venue_id == venues.c.venue_id)
    .scalar_subquery()
)

VENUE_LIST_QUERY = (
    select(
        venues,
        _events_hosted.label("events_hosted"),
        _registrations_count.label("total_registrations"),
        case(
            (_seats_offered > 0, func.round(_registrations_count * 100.0 / _seats_offered, 2)),
            else_=0.0,
        ).label("utilization_percent"),
    )
    .order_by(venues.c.venue_name)
)


@router.get("")
def list_venues(
    session: Session = Depends(get_db),
    search: str | None = Query(default=None),
    availability_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    statement = VENUE_LIST_QUERY
    if search:
        pattern = f"%{search}%"
        statement = statement.where(venues.c.venue_name.ilike(pattern) | venues.c.location.ilike(pattern))
    if availability_status:
        statement = statement.where(venues.c.availability_status == availability_status)
    return apply_pagination(statement, session, page, page_size)


@router.get("/{venue_id}", response_model=VenueRead)
def get_venue(venue_id: int, session: Session = Depends(get_db)):
    row = session.execute(VENUE_LIST_QUERY.where(venues.c.venue_id == venue_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue {venue_id} was not found.")
    return jsonable_rows(rows_as_dicts([row]))[0]


@router.get("/{venue_id}/events")
def venue_events(venue_id: int, session: Session = Depends(get_db)):
    """All events that are scheduled in a venue (used by the venue detail view)."""
    rows = session.execute(
        select(
            events,
            func.count(registrations.c.registration_id).label("registration_count"),
        )
        .select_from(events.outerjoin(registrations, registrations.c.event_id == events.c.event_id))
        .where(events.c.venue_id == venue_id)
        .group_by(events.c.event_id)
        .order_by(events.c.event_date, events.c.start_time)
    ).all()
    return jsonable_rows(rows_as_dicts(rows))


@router.post("", response_model=VenueRead, status_code=status.HTTP_201_CREATED)
def create_venue(payload: VenueCreate, session: Session = Depends(get_db)):
    values = payload.model_dump()
    values["availability_status"] = values["availability_status"].value
    try:
        result = session.execute(venues.insert().values(**values))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="venue")
    return get_venue(int(result.inserted_primary_key[0]), session)


@router.put("/{venue_id}", response_model=VenueRead)
def update_venue(venue_id: int, payload: VenueUpdate, session: Session = Depends(get_db)):
    existing = session.execute(select(venues.c.venue_id).where(venues.c.venue_id == venue_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue {venue_id} was not found.")
    values = payload.model_dump(exclude_none=True)
    if "availability_status" in values:
        values["availability_status"] = values["availability_status"].value
    if values:
        try:
            session.execute(venues.update().where(venues.c.venue_id == venue_id).values(**values))
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise integrity_error(exc, entity="venue")
    return get_venue(venue_id, session)


@router.delete("/{venue_id}")
def delete_venue(venue_id: int, session: Session = Depends(get_db)):
    existing = session.execute(select(venues.c.venue_id).where(venues.c.venue_id == venue_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue {venue_id} was not found.")
    try:
        session.execute(venues.delete().where(venues.c.venue_id == venue_id))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="venue")
    return {"message": f"Venue {venue_id} was deleted."}
