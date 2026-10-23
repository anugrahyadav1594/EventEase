"""Venue and organizer CRUD including the delete protection."""
from __future__ import annotations


def test_venue_crud(client):
    created = client.post(
        "/api/venues",
        json={
            "venue_name": "Test Hall",
            "location": "Block Z",
            "capacity": 120,
            "venue_type": "Seminar Hall",
            "availability_status": "Available",
        },
    )
    assert created.status_code == 201
    venue_id = created.json()["venue_id"]

    listing = client.get("/api/venues", params={"search": "Test Hall"})
    assert listing.json()["total"] == 1

    updated = client.put(f"/api/venues/{venue_id}", json={"availability_status": "Maintenance"})
    assert updated.status_code == 200
    assert updated.json()["availability_status"] == "Maintenance"

    assert client.delete(f"/api/venues/{venue_id}").status_code == 200
    assert client.get(f"/api/venues/{venue_id}").status_code == 404


def test_venue_with_invalid_capacity_is_rejected(client):
    response = client.post(
        "/api/venues",
        json={"venue_name": "Broken Hall", "location": "Nowhere", "capacity": 0},
    )
    assert response.status_code == 422


def test_organizer_crud(client):
    created = client.post(
        "/api/organizers",
        json={
            "organizer_name": "Test Organizer",
            "email": "test.organizer@eventease.edu",
            "phone": "+91-90000-11111",
            "organization_name": "Test Club",
        },
    )
    assert created.status_code == 201
    organizer_id = created.json()["organizer_id"]
    assert created.json()["events_managed"] == 0

    updated = client.put(f"/api/organizers/{organizer_id}", json={"organization_name": "Renamed Club"})
    assert updated.status_code == 200
    assert updated.json()["organization_name"] == "Renamed Club"

    assert client.delete(f"/api/organizers/{organizer_id}").status_code == 200


def test_organizer_with_events_cannot_be_deleted(client):
    response = client.delete("/api/organizers/1")
    assert response.status_code == 409
    assert "referenced" in response.json()["detail"].lower()


def test_venue_with_events_cannot_be_deleted(client):
    response = client.delete("/api/venues/1")
    assert response.status_code == 409


def test_attendee_with_registrations_cannot_be_deleted(client):
    response = client.delete("/api/attendees/1")
    assert response.status_code == 409


def test_venue_events_endpoint(client):
    response = client.get("/api/venues/1/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
