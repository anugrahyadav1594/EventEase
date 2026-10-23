"""Registration endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..schemas import AttendanceUpdate, RegistrationCreate, RegistrationRead, RegistrationStatusUpdate
from ..services.helpers import jsonable_rows
from ..services.registrations import (
    create_registration,
    get_registration_or_404,
    list_registrations,
    mark_attendance,
    update_registration_status,
)

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.get("")
def get_registrations(
    session: Session = Depends(get_db),
    event_id: int | None = Query(default=None),
    attendee_id: int | None = Query(default=None),
    registration_status: str | None = Query(default=None, alias="status"),
    attendance_status: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    rows = list_registrations(
        session,
        event_id=event_id,
        attendee_id=attendee_id,
        status_filter=registration_status,
        attendance_filter=attendance_status,
        search=search,
    )
    return {"items": jsonable_rows(rows), "total": len(rows)}


@router.get("/{registration_id}", response_model=RegistrationRead)
def get_registration(registration_id: int, session: Session = Depends(get_db)):
    row = get_registration_or_404(session, registration_id)
    return jsonable_rows([dict(row._mapping)])[0]


@router.post("", response_model=RegistrationRead, status_code=status.HTTP_201_CREATED)
def post_registration(payload: RegistrationCreate, session: Session = Depends(get_db)):
    row = create_registration(session, payload)
    return jsonable_rows([dict(row)])[0]


@router.patch("/{registration_id}/status", response_model=RegistrationRead)
def patch_registration_status(
    registration_id: int,
    payload: RegistrationStatusUpdate,
    session: Session = Depends(get_db),
):
    row = update_registration_status(session, registration_id, payload.registration_status)
    return jsonable_rows([dict(row)])[0]


@router.patch("/{registration_id}/attendance", response_model=RegistrationRead)
def patch_registration_attendance(
    registration_id: int,
    payload: AttendanceUpdate,
    session: Session = Depends(get_db),
):
    row = mark_attendance(session, registration_id, payload.attendance_status)
    return jsonable_rows([dict(row)])[0]
