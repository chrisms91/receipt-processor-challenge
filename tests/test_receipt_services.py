import pytest
from app.models.receipt import Receipt, Item
from app.services.receipt_services import (
    points_for_retailer_name,
    points_for_round_dollar_amount,
    points_for_multiple_of_25,
    points_for_items_pair,
    points_for_item_descriptions,
    points_for_odd_day,
    points_for_purchase_time,
    calculate_score,
)


def test_points_for_retailer_name():
    assert points_for_retailer_name("Retailer123") == 11
    assert points_for_retailer_name("Retailer!") == 8
    assert points_for_retailer_name("!@**$#@") == 0
    assert points_for_retailer_name("") == 0


def test_points_for_round_dollar_amount():
    assert points_for_round_dollar_amount("10.00") == 50
    assert points_for_round_dollar_amount("0.00") == 50
    assert points_for_round_dollar_amount("10.50") == 0  # Not a round dollar amount
    assert points_for_round_dollar_amount("100.99") == 0  # Not a round dollar amount


def test_points_for_multiple_of_25():
    assert points_for_multiple_of_25("10.25") == 25
    assert points_for_multiple_of_25("10.50") == 25
    assert points_for_multiple_of_25("10.75") == 25
    assert points_for_multiple_of_25("10.30") == 0  # Not a multiple of 0.25


def test_points_for_items_pair():
    item = Item(shortDescription="Gatorade", price="2.25")
    assert points_for_items_pair([item, item]) == 5
    assert points_for_items_pair([item, item, item]) == 5  # 3 items, 1 pair
    assert points_for_items_pair([item, item, item, item]) == 10  # 4 items, 2 pairs
    assert points_for_items_pair([item]) == 0  # 1 item, 0 pair


def test_points_for_item_descriptions():
    items = [
        Item(shortDescription="Mountain Dew 12PK", price="6.49"),
        Item(shortDescription="Emils Cheese Pizza", price="12.25"),
        Item(shortDescription="Knorr Creamy Chicken", price="1.26"),
        Item(shortDescription="Doritos Nacho Cheese", price="3.35"),
        Item(shortDescription="   Klarbrunn 12-PK 12 FL OZ  ", price="12.00"),
    ]
    # "Emils Cheese Pizza" and "Klarbrunn 12-PK 12 FL OZ" are multiples of 3
    # 3 + 3 = 6 points
    assert points_for_item_descriptions(items) == 6

    items = [
        Item(shortDescription="abcdef", price="3.00"),
        Item(shortDescription="abcd", price="4.00"),
    ]
    # "abcdef" is multiple of 3, ceil(3.00 * 0.2) = 1 point
    assert points_for_item_descriptions(items) == 1

    items = [Item(shortDescription="abcd", price="1.00")]
    # "abcd" is not a multiple of 3, 0 point
    assert points_for_item_descriptions(items) == 0

    items = [Item(shortDescription=" ", price="1.00")]
    # 0 is multiple of 3, ceil(1.00 * 0.2) = 1 point
    assert points_for_item_descriptions(items) == 1


def test_points_for_odd_day():
    assert points_for_odd_day("2023-01-01") == 6  # day is odd
    assert points_for_odd_day("2023-01-02") == 0  # day is even


def test_points_for_purchase_time():
    assert points_for_purchase_time("14:30") == 10  # Between 2:00pm and 4:00pm
    assert points_for_purchase_time("14:00") == 0  # Exactly 2:00pm
    assert points_for_purchase_time("16:00") == 0  # Exactly 4:00pm
    assert points_for_purchase_time("13:59") == 0  # Before 2:00pm
    assert points_for_purchase_time("16:01") == 0  # After 4:00pm


def test_calculate_score():
    items = [
        Item(shortDescription="Mountain Dew 12PK", price="6.49"),
        Item(shortDescription="Emils Cheese Pizza", price="12.25"),
        Item(shortDescription="Knorr Creamy Chicken", price="1.26"),
        Item(shortDescription="Doritos Nacho Cheese", price="3.35"),
        Item(shortDescription="   Klarbrunn 12-PK 12 FL OZ  ", price="12.00"),
    ]
    receipt = Receipt(
        retailer="Target",
        total="35.35",
        items=items,
        purchaseDate="2022-01-01",
        purchaseTime="13:01",
    )

    # should be 28
    expected_points = (
        points_for_retailer_name(receipt.retailer)
        + points_for_round_dollar_amount(receipt.total)
        + points_for_multiple_of_25(receipt.total)
        + points_for_items_pair(receipt.items)
        + points_for_item_descriptions(receipt.items)
        + points_for_odd_day(receipt.purchaseDate)
        + points_for_purchase_time(receipt.purchaseTime)
    )

    assert calculate_score(receipt) == expected_points
