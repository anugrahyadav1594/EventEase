"""Registration rules: duplicates, capacity and status transitions."""
from __future__ import annotations

from datetime import date, timedelta

import pytest


@pytest.fixture()
def small_event(client):
    """An event with exactly one free seat."""
    venue = client.post(
        "/api/venues",
        json={
            "venue_name": "Test Chamber",
            "location": "Test Wing",
            "capacity": 5,
            "venue_type": "Lab",
            "availability_status": "Available",
        },
    )
    assert venue.status_code == 201
    venue_id = venue.json()["venue_id"]

    event = client.post(
        "/api/events",
        json={
            "event_name": "Capacity Test Session",
            "description": "Only one seat is available.",
            "event_category": "Technical",
            "organizer_id": 1,
            "venue_id": venue_id,
            "event_date": (date.today() + timedelta(days=120)).isoformat(),
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "capacity": 1,
            "ticket_price": 0,
            "event_status": "Upcoming",
        },
    )
    assert event.status_code == 201
    yield event.json()["event_id"], venue_id
    client.delete(f"/api/events/{event.json()['event_id']}")
    client.delete(f"/api/venues/{venue_id}")


def test_register_attendee_for_event(client):
    response = client.post("/api/registrations", json={"attendee_id": 1, "event_id": 16})
    assert response.status_code in (201, 409)

    # attendee 1 is already registered for event 16 in the demo data -> duplicate
    duplicate = client.post("/api/registrations", json={"attendee_id": 1, "event_id": 16})
    assert duplicate.status_code == 409
    assert "already registered" in duplicate.json()["detail"].lower()


def test_registration_beyond_capacity_is_rejected(client, small_event):
    event_id, _ = small_event

    first = client.post("/api/registrations", json={"attendee_id": 1, "event_id": event_id})
    assert first.status_code == 201, first.text
    registration_id = first.json()["registration_id"]

    second = client.post("/api/registrations", json={"attendee_id": 2, "event_id": event_id})
    assert second.status_code == 409
    assert "full" in second.json()["detail"].lower()

    # Cancelling the first registration frees the seat again.
    cancelled = client.patch(
        f"/api/registrations/{registration_id}/status",
        json={"registration_status": "Cancelled"},
    )
    assert cancelled.status_code == 200
    third = client.post("/api/registrations", json={"attendee_id": 2, "event_id": event_id})
    assert third.status_code == 201


def test_registration_with_invalid_foreign_key(client):
    response = client.post("/api/registrations", json={"attendee_id": 987654, "event_id": 16})
    assert response.status_code == 404

    response = client.post("/api/registrations", json={"attendee_id": 1, "event_id": 987654})
    assert response.status_code == 404


def test_registration_status_and_attendance_updates(client):
    listing = client.get("/api/registrations", params={"status": "Registered"})
    assert listing.status_code == 200
    registration = listing.json()["items"][0]
    registration_id = registration["registration_id"]

    confirmed = client.patch(
        f"/api/registrations/{registration_id}/status",
        json={"registration_status": "Confirmed"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["registration_status"] == "Confirmed"

    present = client.patch(
        f"/api/registrations/{registration_id}/attendance",
        json={"attendance_status": "Present"},
    )
    assert present.status_code == 200
    assert present.json()["attendance_status"] == "Present"

    absent = client.patch(
        f"/api/registrations/{registration_id}/attendance",
        json={"attendance_status": "Absent"},
    )
    assert absent.status_code == 200
    assert absent.json()["attendance_status"] == "Absent"


def test_invalid_status_transition_is_rejected(client):
    listing = client.get("/api/registrations", params={"status": "Cancelled"})
    registration = listing.json()["items"][0]
    response = client.patch(
        f"/api/registrations/{registration['registration_id']}/status",
        json={"registration_status": "Confirmed"},
    )
    assert response.status_code == 409


def test_attendance_for_cancelled_registration_is_rejected(client):
    listing = client.get("/api/registrations", params={"status": "Cancelled"})
    registration = listing.json()["items"][0]
    response = client.patch(
        f"/api/registrations/{registration['registration_id']}/attendance",
        json={"attendance_status": "Present"},
    )
    assert response.status_code == 409
