"""Event CRUD endpoints."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..models import events
from ..schemas import EventCreate, EventRead, EventUpdate
from ..services.events import (
    assert_capacity_not_below_registered,
    assert_organizer_exists,
    assert_capacity_within_venue,
    assert_venue_available,
    event_summary,
    get_event_or_404,
    list_events,
)
from ..services.helpers import apply_pagination, integrity_error, jsonable_rows, rows_as_dicts

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def get_events(
    session: Session = Depends(get_db),
    search: str | None = Query(default=None, description="Search by name, description or category"),
    category: str | None = Query(default=None),
    event_status: str | None = Query(default=None, alias="status"),
    organizer_id: int | None = Query(default=None),
    venue_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    rows = list_events(
        session,
        search=search,
        category=category,
        status_filter=event_status,
        organizer_id=organizer_id,
        venue_id=venue_id,
        date_from=date_from,
        date_to=date_to,
    )
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]
    items = [event_summary(session, row) for row in page_rows]
    return {
        "items": items,
        "total": len(rows),
        "page": page,
        "page_size": page_size,
        "pages": max(1, -(-len(rows) // page_size)),
    }


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, session: Session = Depends(get_db)):
    row = get_event_or_404(session, event_id)
    return event_summary(session, dict(row._mapping))


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, session: Session = Depends(get_db)):
    values = payload.model_dump()
    values["event_status"] = values["event_status"].value
    values["ticket_price"] = values["ticket_price"]

    assert_organizer_exists(session, values["organizer_id"])
    assert_capacity_within_venue(session, values["venue_id"], values["capacity"])
    assert_venue_available(
        session,
        values["venue_id"],
        values["event_date"],
        values["start_time"],
        values["end_time"],
    )

    try:
        result = session.execute(events.insert().values(**values))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="event")
    return get_event(int(result.inserted_primary_key[0]), session)


@router.put("/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, session: Session = Depends(get_db)):
    row = get_event_or_404(session, event_id)
    current = dict(row._mapping)
    values = payload.model_dump(exclude_none=True)
    if "event_status" in values:
        values["event_status"] = values["event_status"].value

    merged = {
        "organizer_id": values.get("organizer_id", current["organizer_id"]),
        "venue_id": values.get("venue_id", current["venue_id"]),
        "capacity": values.get("capacity", current["capacity"]),
        "event_date": values.get("event_date", current["event_date"]),
        "start_time": values.get("start_time", current["start_time"]),
        "end_time": values.get("end_time", current["end_time"]),
    }
    if merged["start_time"] >= merged["end_time"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be later than start_time.",
        )

    assert_organizer_exists(session, merged["organizer_id"])
    assert_capacity_within_venue(session, merged["venue_id"], merged["capacity"])
    assert_venue_available(
        session,
        merged["venue_id"],
        merged["event_date"],
        merged["start_time"],
        merged["end_time"],
        event_id=event_id,
    )
    assert_capacity_not_below_registered(session, event_id, merged["capacity"])

    if values:
        try:
            session.execute(events.update().where(events.c.event_id == event_id).values(**values))
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise integrity_error(exc, entity="event")
    return get_event(event_id, session)


@router.delete("/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_db)):
    existing = session.execute(select(events.c.event_id).where(events.c.event_id == event_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} was not found.")
    try:
        session.execute(events.delete().where(events.c.event_id == event_id))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="event")
    return {"message": f"Event {event_id} was deleted."}
