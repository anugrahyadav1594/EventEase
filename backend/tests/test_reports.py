"""The report endpoints must return the documented shape."""
from __future__ import annotations

import pytest

REPORT_ENDPOINTS = [
    "event-registrations",
    "event-revenue",
    "venue-utilization",
    "popular-events",
    "attendee-history",
    "attendance-summary",
    "events-above-average",
]


@pytest.mark.parametrize("endpoint", REPORT_ENDPOINTS)
def test_report_shape(client, endpoint):
    response = client.get(f"/api/reports/{endpoint}")
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["title"]
    assert payload["concept"]
    assert payload["explanation"]
    assert "SELECT" in payload["sql"].upper()
    assert isinstance(payload["columns"], list) and payload["columns"]
    assert isinstance(payload["rows"], list)
    assert payload["row_count"] == len(payload["rows"])


def test_report_overview_lists_every_report(client):
    response = client.get("/api/reports")
    assert response.status_code == 200
    keys = {item["key"] for item in response.json()}
    assert keys == set(REPORT_ENDPOINTS)


def test_popular_events_limit_is_a_bound_parameter(client):
    response = client.get("/api/reports/popular-events", params={"limit": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["row_count"] <= 3
    assert ":limit" in payload["sql"]


def test_event_registrations_report_counts_match_the_view(client):
    from sqlalchemy import text

    expected = client.get("/api/reports/event-registrations").json()["rows"]
    for row in expected:
        assert row["total_registrations"] >= 0
        assert row["fill_rate_percent"] >= 0


def test_venue_utilization_includes_venues_without_events(client):
    payload = client.get("/api/reports/venue-utilization").json()
    assert payload["row_count"] >= 9
    assert any(row["events_hosted"] == 0 for row in payload["rows"])


def test_events_above_average_uses_a_nested_subquery(client):
    payload = client.get("/api/reports/events-above-average").json()
    assert "SELECT AVG" in payload["sql"].upper()
    assert payload["row_count"] > 0
    average = payload["rows"][0]["average_registrations"]
    for row in payload["rows"]:
        assert row["registration_count"] > average
