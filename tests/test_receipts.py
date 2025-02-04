import pytest
from fastapi import status
from app.models.receipt import Receipt
from app.main import app


def test_process_receipt_valid(test_client):
    payload = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
            {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
        ],
        "total": "35.35",
    }
    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data


def test_process_receipt_missing_field(test_client):
    # Missing the 'retailer' field.
    payload = {
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [{"shortDescription": "Mountain Dew 12PK", "price": "6.49"}],
        "total": "35.35",
    }
    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_receipt_points(test_client):
    payload = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
        ],
        "total": "9.00",
    }
    valid_score = 109

    post_response = test_client.post("/receipts/process", json=payload)
    assert post_response.status_code == status.HTTP_200_OK

    receipt_id = post_response.json()["id"]
    get_response = test_client.get(f"/receipts/{receipt_id}/points")
    assert get_response.status_code == status.HTTP_200_OK

    data = get_response.json()
    assert data["points"] == valid_score
