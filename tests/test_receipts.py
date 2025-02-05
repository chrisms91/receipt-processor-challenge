import pytest
from uuid import uuid4
from fastapi import status
from app.models.receipt import Receipt


# --- Valid Path Tests ---


def test_receipt_submission(test_client):
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
    assert isinstance(data["id"], str)


def test_get_receipt_points(test_client):
    payload = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
            {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
            {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
            {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
            {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"},
        ],
        "total": "35.35",
    }
    post_response = test_client.post("/receipts/process", json=payload)
    assert post_response.status_code == status.HTTP_200_OK
    receipt_id = post_response.json()["id"]

    get_response = test_client.get(f"/receipts/{receipt_id}/points")
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert "points" in data
    assert isinstance(data["points"], int)


# --- Validation Tests ---


def test_invalid_purchase_date_format(test_client):
    payload = {
        "retailer": "Fetch Rewards",
        "purchaseDate": "05/01/2022",  # Incorrect format; should be YYYY-MM-DD
        "purchaseTime": "15:00",
        "items": [{"shortDescription": "Item A", "price": "10.00"}],
        "total": "10.00",
    }

    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_invalid_purchase_time_format(test_client):
    payload = {
        "retailer": "Fetch Rewards",
        "purchaseDate": "2022-05-01",
        "purchaseTime": "3:00 PM",  # Incorrect format; should be HH:MM (24-hour)
        "items": [{"shortDescription": "Item A", "price": "10.00"}],
        "total": "10.00",
    }
    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_invalid_price_format(test_client):
    payload = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "two dollars"}
        ],  # Incorrect price format
        "total": "2.25",
    }
    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --- Edge/Error Handling Tests ---


def test_missing_required_field(test_client):
    payload = {
        # "retailer" is missing intentionally.
        "purchaseDate": "2022-05-01",
        "purchaseTime": "15:00",
        "items": [{"shortDescription": "Item A", "price": "10.00"}],
        "total": "10.00",
    }
    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_receipt_with_no_items(test_client):
    payload = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [],  # empty items
        "total": "2.25",
    }
    response = test_client.post("/receipts/process", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_points_nonexistent_receipt(test_client):
    fake_id = str(uuid4())
    response = test_client.get(f"/receipts/{fake_id}/points")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_duplicate_receipt_processed_once(test_client):
    payload = {
        "retailer": "Duplicate Test Store",
        "purchaseDate": "2022-05-01",
        "purchaseTime": "15:00",
        "items": [{"shortDescription": "Test Item", "price": "10.00"}],
        "total": "10.00",
    }

    response_origin = test_client.post("/receipts/process", json=payload)
    assert response_origin.status_code == status.HTTP_200_OK
    receipt_id_origin = response_origin.json()["id"]
    assert receipt_id_origin

    # duplicate submission of the same receipt payload
    response_dup = test_client.post("/receipts/process", json=payload)
    assert response_dup.status_code == status.HTTP_200_OK
    receipt_id_dup = response_dup.json()["id"]
    assert receipt_id_dup

    # ensure both submissions return the same id.
    assert receipt_id_origin == receipt_id_dup
