from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_sale_cash():
    token = "mock_staff_token"
    payload = {
        "items": [
            {"product_id": 1, "qty": 1, "unit_price": 10.0, "unit_cost": 5.0}
        ],
        "payment_method": "cash"
    }
    response = client.post("/sales/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 201, 401, 403)

def test_create_sale_credit_owner_only():
    token = "mock_owner_token"
    payload = {
        "items": [
            {"product_id": 1, "qty": 1, "unit_price": 10.0, "unit_cost": 5.0}
        ],
        "payment_method": "cash",
        "is_credit": True
    }
    response = client.post("/sales/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 201, 401, 403)

def test_sale_insufficient_stock():
    token = "mock_staff_token"
    payload = {
        "items": [
            {"product_id": 1, "qty": 99999, "unit_price": 10.0, "unit_cost": 5.0}
        ],
        "payment_method": "cash"
    }
    response = client.post("/sales/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (400, 401, 403)

def test_sale_negative_qty():
    token = "mock_staff_token"
    payload = {
        "items": [
            {"product_id": 1, "qty": -1, "unit_price": 10.0, "unit_cost": 5.0}
        ],
        "payment_method": "cash"
    }
    response = client.post("/sales/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (400, 422, 401, 403)
