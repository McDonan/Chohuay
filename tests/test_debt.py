import os

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def _owner_auth_headers():
    token = os.environ.get("TEST_OWNER_TOKEN")
    if not token:
        pytest.skip("TEST_OWNER_TOKEN must be set to a valid owner token for authenticated debt tests")
    return {"Authorization": f"Bearer {token}"}

def test_pay_debt_success():
    # Assume customer_id=1 exists and has debt in the test environment.
    response = client.post(
        "/debt/payment",
        json={"customer_id": 1, "amount": 100, "note": "partial payment"},
        headers=_owner_auth_headers()
    )
    assert response.status_code == 200

def test_pay_debt_overpayment():
    response = client.post(
        "/debt/payment",
        json={"customer_id": 1, "amount": 999999, "note": "overpay"},
        headers=_owner_auth_headers()
    )
    assert response.status_code == 400

def test_pay_debt_invalid_customer():
    response = client.post(
        "/debt/payment",
        json={"customer_id": 9999, "amount": 50},
        headers=_owner_auth_headers()
    )
    assert response.status_code == 404

def test_get_customer_debt():
    response = client.get(
        "/debt/customer/1",
        headers=_owner_auth_headers()
    )
    assert response.status_code in (200, 404)
