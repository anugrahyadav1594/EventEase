"""Health check and dashboard endpoint."""
from __future__ import annotations


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database_connected"] is True
    assert payload["row_counts"]["events"] > 0
    assert payload["row_counts"]["attendees"] > 0


def test_dashboard_endpoint(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    payload = response.json()

    metrics = payload["metrics"]
    assert metrics["total_events"] == 20
    assert metrics["total_registrations"] > 0
    assert metrics["upcoming_events"] >= 1
    assert metrics["completed_events"] >= 1
    assert metrics["total_revenue"] > 0
    assert 0 <= metrics["average_attendance_rate"] <= 100

    charts = payload["charts"]
    assert charts["registrations_by_event"]
    assert charts["revenue_by_category"]
    assert charts["attendance_by_event"]
    assert charts["venue_utilization"]

    assert payload["upcoming_schedule"]
    assert payload["popular_events"]
