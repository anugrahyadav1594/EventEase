"""Attendee CRUD and the duplicate e-mail rule."""
from __future__ import annotations


def _attendee_payload(**overrides) -> dict:
    payload = {
        "full_name": "Test Attendee",
        "email": "test.attendee@student.edu",
        "phone": "+91-99999-00000",
        "organization": "Test Department",
    }
    payload.update(overrides)
    return payload


def test_create_and_read_attendee(client):
    response = client.post("/api/attendees", json=_attendee_payload())
    assert response.status_code == 201, response.text
    attendee = response.json()
    attendee_id = attendee["attendee_id"]
    assert attendee["email"] == "test.attendee@student.edu"
    assert attendee["total_registrations"] == 0

    fetched = client.get(f"/api/attendees/{attendee_id}")
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Test Attendee"

    listing = client.get("/api/attendees", params={"search": "Test Attendee"})
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    updated = client.put(f"/api/attendees/{attendee_id}", json={"full_name": "Renamed Attendee"})
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Renamed Attendee"

    assert client.delete(f"/api/attendees/{attendee_id}").status_code == 200
    assert client.get(f"/api/attendees/{attendee_id}").status_code == 404


def test_duplicate_attendee_email_is_rejected(client):
    first = client.post("/api/attendees", json=_attendee_payload())
    assert first.status_code == 201
    attendee_id = first.json()["attendee_id"]

    duplicate = client.post(
        "/api/attendees",
        json=_attendee_payload(full_name="Another Person", email="test.attendee@student.edu"),
    )
    assert duplicate.status_code == 409
    assert "unique" in duplicate.json()["detail"].lower()

    client.delete(f"/api/attendees/{attendee_id}")


def test_invalid_attendee_payload_is_rejected(client):
    response = client.post("/api/attendees", json={"full_name": "x", "email": "not-an-email"})
    assert response.status_code == 422


def test_attendee_registration_history(client):
    response = client.get("/api/attendees/1/registrations")
    assert response.status_code == 200
    history = response.json()
    assert history
    assert all(item["attendee_id"] == 1 for item in history)
