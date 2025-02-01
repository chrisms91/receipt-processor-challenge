import pytest
from fastapi.testclient import TestClient
from service import calculate_score, process_receipt
from models import Receipt
from main import app

client = TestClient(app)

valid_payload = {
    "retailer": "M&M Corner Market",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "15:01",
    "items": [{"shortDescription": "Mountain Dew 12PK", "price": "6.49"}],
    "total": "6.49",
}

valid_score = 30


def test_process_receipt_valid():
    response = client.post("/receipts/process", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


def test_get_receipt_points():
    post_response = client.post("/receipts/process", json=valid_payload)
    assert post_response.status_code == 200
    receipt_id = post_response.json()["id"]

    get_response = client.get(f"/receipts/{receipt_id}/points")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["points"] == valid_score
