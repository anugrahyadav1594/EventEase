"""Payment handling and revenue calculation."""
from __future__ import annotations

from decimal import Decimal


def _first_registration_id(client) -> int:
    payload = client.get("/api/registrations", params={"page": 1}).json()
    return payload["items"][0]["registration_id"]


def test_create_payment_and_update_status(client):
    registration_id = _first_registration_id(client)
    response = client.post(
        "/api/payments",
        json={
            "registration_id": registration_id,
            "amount": 500,
            "payment_method": "UPI",
            "payment_status": "Pending",
            "transaction_reference": "TEST-TXN-0001",
        },
    )
    assert response.status_code == 201, response.text
    payment = response.json()
    payment_id = payment["payment_id"]
    assert payment["payment_status"] == "Pending"
    assert Decimal(str(payment["amount"])) == Decimal("500")

    completed = client.patch(f"/api/payments/{payment_id}/status", json={"payment_status": "Completed"})
    assert completed.status_code == 200
    assert completed.json()["payment_status"] == "Completed"

    refunded = client.patch(f"/api/payments/{payment_id}/status", json={"payment_status": "Refunded"})
    assert refunded.status_code == 200
    assert refunded.json()["payment_status"] == "Refunded"

    # A refunded payment can not be completed again.
    invalid = client.patch(f"/api/payments/{payment_id}/status", json={"payment_status": "Completed"})
    assert invalid.status_code == 409


def test_duplicate_transaction_reference_is_rejected(client):
    registration_id = _first_registration_id(client)
    payload = {
        "registration_id": registration_id,
        "amount": 100,
        "payment_method": "Cash",
        "payment_status": "Completed",
        "transaction_reference": "TEST-TXN-0002",
    }
    assert client.post("/api/payments", json=payload).status_code == 201
    duplicate = client.post("/api/payments", json=payload)
    assert duplicate.status_code == 409


def test_negative_amount_is_rejected(client):
    registration_id = _first_registration_id(client)
    response = client.post(
        "/api/payments",
        json={
            "registration_id": registration_id,
            "amount": -50,
            "payment_method": "Cash",
        },
    )
    assert response.status_code == 422


def test_payment_for_unknown_registration_is_rejected(client):
    response = client.post(
        "/api/payments",
        json={"registration_id": 987654, "amount": 10, "payment_method": "Cash"},
    )
    assert response.status_code == 404


def test_revenue_counts_completed_payments_only(client, db_session):
    from sqlalchemy import text

    expected = db_session.execute(
        text("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status = 'Completed'")
    ).scalar()
    expected_refunded = db_session.execute(
        text("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status = 'Refunded'")
    ).scalar()

    report = client.get("/api/reports/event-revenue").json()
    report_total = sum(Decimal(str(row["gross_revenue"])) for row in report["rows"])
    refunded_total = sum(Decimal(str(row["refunded_amount"])) for row in report["rows"])

    assert report_total == Decimal(str(expected))
    assert refunded_total == Decimal(str(expected_refunded))

    dashboard = client.get("/api/dashboard").json()
    assert Decimal(str(dashboard["metrics"]["total_revenue"])) == Decimal(str(expected))
    assert Decimal(str(dashboard["metrics"]["refunded_amount"])) == Decimal(str(expected_refunded))
