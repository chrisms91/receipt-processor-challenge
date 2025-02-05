import pytest
from uuid import uuid4
from fastapi import status
from app.models.receipt import Receipt


# --- Fixtures for Common Payloads ---
@pytest.fixture
def base_payload():
    return {
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


# --- Valid Path Tests ---


def test_receipt_submission(test_client, base_payload):
    response = test_client.post("/receipts/process", json=base_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], str)


def test_get_receipt_points(test_client, base_payload):
    post_response = test_client.post("/receipts/process", json=base_payload)
    assert post_response.status_code == status.HTTP_200_OK
    receipt_id = post_response.json()["id"]

    get_response = test_client.get(f"/receipts/{receipt_id}/points")
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert "points" in data
    assert isinstance(data["points"], int)
    expected_points = 28
    assert data["points"] == expected_points


# --- Validation Tests ---


@pytest.mark.parametrize(
    "field, invalid_value, error_loc",
    [
        ("purchaseDate", "05/01/2022", "purchaseDate"),
        ("purchaseTime", "3:00 PM", "purchaseTime"),
        ("purchaseTime", "25:00", "purchaseTime"),
        ("total", "-5.00", "total"),
        (
            "items",
            [{"shortDescription": "Emils Cheese Pizza", "price": "five dollars"}],
            "price",
        ),
    ],
)
def test_invalid_formats(test_client, base_payload, field, invalid_value, error_loc):
    base_payload[field] = invalid_value
    response = test_client.post("/receipts/process", json=base_payload)
    errors = response.json()["errors"]
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_loc in errors[0]["loc"]


@pytest.mark.parametrize(
    "missing_field", ["retailer", "purchaseDate", "purchaseTime", "items", "total"]
)
def test_missing_receipt_required_fields(test_client, base_payload, missing_field):

    del base_payload[missing_field]
    response = test_client.post("/receipts/process", json=base_payload)
    errors = response.json()["errors"]
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in errors[0]["loc"]


@pytest.mark.parametrize("missing_field", ["shortDescription", "price"])
def test_missing_item_required_fields(test_client, base_payload, missing_field):
    del base_payload["items"][0][missing_field]

    response = test_client.post("/receipts/process", json=base_payload)
    errors = response.json()["errors"]
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in errors[0]["loc"]


# --- Edge/Error Handling Tests ---


def test_receipt_with_no_items(test_client, base_payload):
    base_payload["items"] = []  # empty items

    response = test_client.post("/receipts/process", json=base_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_points_nonexistent_receipt(test_client):
    fake_id = str(uuid4())
    response = test_client.get(f"/receipts/{fake_id}/points")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_duplicate_receipt_processed_once(test_client, base_payload):
    response_origin = test_client.post("/receipts/process", json=base_payload)
    assert response_origin.status_code == status.HTTP_200_OK
    receipt_id_origin = response_origin.json()["id"]
    assert receipt_id_origin

    response_dup = test_client.post("/receipts/process", json=base_payload)
    assert response_dup.status_code == status.HTTP_200_OK
    receipt_id_dup = response_dup.json()["id"]
    assert receipt_id_dup

    # duplicate receipts should return the same id.
    assert receipt_id_origin == receipt_id_dup
