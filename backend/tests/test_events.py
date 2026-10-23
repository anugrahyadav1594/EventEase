"""Event CRUD, validation and venue booking rules."""
from __future__ import annotations

from datetime import date, timedelta


def _event_payload(**overrides) -> dict:
    payload = {
        "event_name": "Test Automation Workshop",
        "description": "Created by the automated test suite.",
        "event_category": "Workshop",
        "organizer_id": 1,
        "venue_id": 9,
        "event_date": (date.today() + timedelta(days=90)).isoformat(),
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "capacity": 20,
        "ticket_price": 100,
        "event_status": "Upcoming",
    }
    payload.update(overrides)
    return payload


def test_create_and_read_event(client):
    response = client.post("/api/events", json=_event_payload())
    assert response.status_code == 201, response.text
    event = response.json()
    event_id = event["event_id"]
    assert event["event_name"] == "Test Automation Workshop"
    assert event["venue_name"]
    assert event["organizer_name"]

    fetched = client.get(f"/api/events/{event_id}")
    assert fetched.status_code == 200
    assert fetched.json()["event_id"] == event_id

    listing = client.get("/api/events", params={"search": "Test Automation"})
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    assert client.delete(f"/api/events/{event_id}").status_code == 200
    assert client.get(f"/api/events/{event_id}").status_code == 404


def test_event_capacity_cannot_exceed_venue_capacity(client):
    response = client.post("/api/events", json=_event_payload(capacity=9999, venue_id=9))
    assert response.status_code == 422
    assert "capacity" in response.json()["detail"].lower()


def test_overlapping_venue_bookings_are_rejected(client):
    first = client.post("/api/events", json=_event_payload())
    assert first.status_code == 201
    event_id = first.json()["event_id"]

    clash = client.post(
        "/api/events",
        json=_event_payload(
            event_name="Overlapping Session",
            start_time="11:00:00",
            end_time="13:00:00",
        ),
    )
    assert clash.status_code == 409
    assert "already booked" in clash.json()["detail"].lower()

    # A booking directly after the first event is allowed again.
    later = client.post(
        "/api/events",
        json=_event_payload(
            event_name="Later Session",
            start_time="12:00:00",
            end_time="13:30:00",
        ),
    )
    assert later.status_code == 201
    client.delete(f"/api/events/{later.json()['event_id']}")
    client.delete(f"/api/events/{event_id}")


def test_event_with_invalid_foreign_key_is_rejected(client):
    response = client.post("/api/events", json=_event_payload(venue_id=987654))
    assert response.status_code == 404

    response = client.post("/api/events", json=_event_payload(organizer_id=987654))
    assert response.status_code == 404


def test_event_with_invalid_time_window_is_rejected(client):
    response = client.post(
        "/api/events",
        json=_event_payload(start_time="12:00:00", end_time="10:00:00"),
    )
    assert response.status_code == 422


def test_event_filters(client):
    technical = client.get("/api/events", params={"category": "Technical"})
    assert technical.status_code == 200
    assert all(item["event_category"] == "Technical" for item in technical.json()["items"])

    upcoming = client.get("/api/events", params={"status": "Upcoming"})
    assert upcoming.status_code == 200
    assert all(item["event_status"] == "Upcoming" for item in upcoming.json()["items"])

    paginated = client.get("/api/events", params={"page": 1, "page_size": 3})
    assert paginated.status_code == 200
    body = paginated.json()
    assert len(body["items"]) <= 3
    assert body["page"] == 1 and body["page_size"] == 3
