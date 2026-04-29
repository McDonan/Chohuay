
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    # Replace with a valid PIN for your test DB
    response = client.post("/auth/login", json={"pin": "1234"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure():
    response = client.post("/auth/login", json={"pin": "wrong"})
    assert response.status_code == 401


def test_login_inactive_user():
    # Simulate inactive user (requires test DB setup)
    pytest.skip("Requires test DB fixture for an inactive user scenario")


def test_token_tampering():
    token = get_token("1234")
    if not token:
        pytest.skip("Valid test user with PIN '1234' required")

    parts = token.split(".")
    if len(parts) == 3 and parts[2]:
        tampered_signature = parts[2][:-1] + ("A" if parts[2][-1] != "A" else "B")
        tampered_token = ".".join([parts[0], parts[1], tampered_signature])
    else:
        tampered_token = token + "tampered"

    headers = {"Authorization": f"Bearer {tampered_token}"}
    response = client.post(
        "/auth/change-pin",
        json={"old_pin": "1234", "new_pin": "5678"},
        headers=headers,
    )
    assert response.status_code in (401, 403)
def get_token(pin):
    response = client.post("/auth/login", json={"pin": pin})
    return response.json().get("access_token") if response.status_code == 200 else None

def test_change_pin_success():
    # This test assumes the PIN '1234' exists and is valid
    token = get_token("1234")
    if not token:
        pytest.skip("Valid test user with PIN '1234' required")
    headers = {"Authorization": f"Bearer {token}"}
    # Change PIN to '5678'
    response = client.post("/auth/change-pin", json={"old_pin": "1234", "new_pin": "5678"}, headers=headers)
    assert response.status_code == 200
    # Change it back for idempotency
    token2 = get_token("5678")
    if token2:
        headers2 = {"Authorization": f"Bearer {token2}"}
        client.post("/auth/change-pin", json={"old_pin": "5678", "new_pin": "1234"}, headers=headers2)

def test_change_pin_wrong_old():
    token = get_token("1234")
    if not token:
        pytest.skip("Valid test user with PIN '1234' required")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/change-pin", json={"old_pin": "wrong", "new_pin": "5678"}, headers=headers)
    assert response.status_code == 401

def test_change_pin_short_new():
    token = get_token("1234")
    if not token:
        pytest.skip("Valid test user with PIN '1234' required")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/change-pin", json={"old_pin": "1234", "new_pin": "12"}, headers=headers)
    assert response.status_code == 400
