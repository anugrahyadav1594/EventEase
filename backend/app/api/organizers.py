"""Organizer CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..models import events, organizers, registrations
from ..schemas import OrganizerCreate, OrganizerRead, OrganizerUpdate
from ..services.helpers import apply_pagination, integrity_error, jsonable_rows, rows_as_dicts

router = APIRouter(prefix="/organizers", tags=["organizers"])

ORGANIZER_LIST_QUERY = (
    select(
        organizers,
        func.count(func.distinct(events.c.event_id)).label("events_managed"),
        func.count(func.distinct(registrations.c.registration_id)).label("total_registrations"),
    )
    .select_from(
        organizers.outerjoin(events, events.c.organizer_id == organizers.c.organizer_id).outerjoin(
            registrations, registrations.c.event_id == events.c.event_id
        )
    )
    .group_by(organizers.c.organizer_id)
    .order_by(organizers.c.organizer_name)
)


@router.get("")
def list_organizers(
    session: Session = Depends(get_db),
    search: str | None = Query(default=None, description="Search by name, e-mail or organisation"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    statement = ORGANIZER_LIST_QUERY
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            organizers.c.organizer_name.ilike(pattern)
            | organizers.c.email.ilike(pattern)
            | organizers.c.organization_name.ilike(pattern)
        )
    return apply_pagination(statement, session, page, page_size)


@router.get("/{organizer_id}", response_model=OrganizerRead)
def get_organizer(organizer_id: int, session: Session = Depends(get_db)):
    row = session.execute(ORGANIZER_LIST_QUERY.where(organizers.c.organizer_id == organizer_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organizer {organizer_id} was not found.")
    return jsonable_rows(rows_as_dicts([row]))[0]


@router.post("", response_model=OrganizerRead, status_code=status.HTTP_201_CREATED)
def create_organizer(payload: OrganizerCreate, session: Session = Depends(get_db)):
    try:
        result = session.execute(organizers.insert().values(**payload.model_dump()))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="organizer")
    return get_organizer(int(result.inserted_primary_key[0]), session)


@router.put("/{organizer_id}", response_model=OrganizerRead)
def update_organizer(organizer_id: int, payload: OrganizerUpdate, session: Session = Depends(get_db)):
    existing = session.execute(select(organizers.c.organizer_id).where(organizers.c.organizer_id == organizer_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organizer {organizer_id} was not found.")
    values = payload.model_dump(exclude_none=True)
    if values:
        try:
            session.execute(organizers.update().where(organizers.c.organizer_id == organizer_id).values(**values))
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise integrity_error(exc, entity="organizer")
    return get_organizer(organizer_id, session)


@router.delete("/{organizer_id}")
def delete_organizer(organizer_id: int, session: Session = Depends(get_db)):
    existing = session.execute(select(organizers.c.organizer_id).where(organizers.c.organizer_id == organizer_id)).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organizer {organizer_id} was not found.")
    try:
        session.execute(organizers.delete().where(organizers.c.organizer_id == organizer_id))
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise integrity_error(exc, entity="organizer")
    return {"message": f"Organizer {organizer_id} was deleted."}
