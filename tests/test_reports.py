from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def assert_successful_json_response(response):
    assert response.status_code == 200, response.text
    assert response.headers.get("content-type", "").startswith("application/json")
    payload = response.json()
    assert isinstance(payload, (dict, list))

def test_daily_report():
    token = "mock_owner_token"
    response = client.get("/reports/daily", headers={"Authorization": f"Bearer {token}"})
    assert_successful_json_response(response)

def test_low_stock_alert():
    token = "mock_owner_token"
    response = client.get("/reports/low-stock", headers={"Authorization": f"Bearer {token}"})
    assert_successful_json_response(response)

def test_top_products():
    token = "mock_owner_token"
    response = client.get("/reports/top-products", headers={"Authorization": f"Bearer {token}"})
    assert_successful_json_response(response)

def test_report_large_date_range():
    token = "mock_owner_token"
    response = client.get("/reports/daily?start=2020-01-01&end=2030-01-01", headers={"Authorization": f"Bearer {token}"})
    assert_successful_json_response(response)
