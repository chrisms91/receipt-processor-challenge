import math
from typing import List
from uuid import uuid4
from datetime import time
from app.models.receipt import Receipt, Item
from app.utills import safe_float, safe_datetime, generate_receipt_hash

# in-memory store mapping receipt_id to its computed score
receipt_score_store = {}
# in-memory store mapping hash to uuid to check duplicate receipts
receipt_hash_store = {}


def process_receipt(receipt: Receipt) -> str:
    """
    Process receipt and calculate its score
    storing the score in the memory, and returning the receipt_id generated
    """
    receipt_hash = generate_receipt_hash(receipt)
    if receipt_hash in receipt_hash_store:
        # Receipt already exists. Returning the existing ID
        return receipt_hash_store[receipt_hash]

    receipt_id = str(uuid4())
    score = calculate_score(receipt)
    receipt_hash_store[receipt_hash] = receipt_id
    receipt_score_store[receipt_id] = score
    return receipt_id


def get_score(receipt_id: str) -> int:
    """
    Retrieve score from the memory for the given receipt_id
    Return None if receipt_id doesn't exist
    """
    return receipt_score_store.get(receipt_id)


def calculate_score(receipt: Receipt) -> int:
    """
    Calculate points for a given receipt.

    Rules:
    - 1 point for every alphanumeric chars in the retailer name.
    - 50 points if the total is a round dollar amount with no cents. (e.g. 10.00)
    - 25 points if the total is a multiple of 0.25.
    - 5 points for every two items on the receipt.
    - For each item: if the trimmed description length is a multiple of 3,
        multiply the price by 0.2 and round up to the nearest integer, then add that many points.
    - 6 points if the day in the purchase date is odd
    - 10 points if the time of the purchase is after 2:00pm and before 4:00pm
    """

    total_points = 0
    total_points += points_for_retailer_name(receipt.retailer)
    total_points += points_for_round_dollar_amount(receipt.total)
    total_points += points_for_multiple_of_25(receipt.total)
    total_points += points_for_items_pair(receipt.items)
    total_points += points_for_item_descriptions(receipt.items)
    total_points += points_for_odd_day(receipt.purchaseDate)
    total_points += points_for_purchase_time(receipt.purchaseTime)

    return total_points


def points_for_retailer_name(retailer: str) -> int:
    """
    1 point for every alphanumeric character in the retailer name.
    """
    points = 0
    for char in retailer:
        if char.isalnum():
            points += 1
    return points


def points_for_round_dollar_amount(total: str) -> int:
    """
    50 points if the total is a round dollar amount with no cents.
    """
    return 50 if total.endswith(".00") else 0


def points_for_multiple_of_25(total: str) -> int:
    """
    25 points if the total is a multiple of 0.25.
    """
    total_float = safe_float(total, "total")
    return 25 if total_float % 0.25 == 0 else 0


def points_for_items_pair(items: List[Item]) -> int:
    """
    5 points for every two items on the receipt.
    """
    num_pairs = len(items) // 2
    return num_pairs * 5


def points_for_item_descriptions(items: List[Item]) -> int:
    """
    If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer
    """
    points = 0
    for item in items:
        short_desc = item.shortDescription.strip()
        if len(short_desc) % 3 == 0:
            price = safe_float(item.price, "price for item")
            points_from_item = math.ceil(price * 0.2)
            points += points_from_item
    return points


def points_for_odd_day(purchase_date: str) -> int:
    """
    6 points if the day in the purchase date is odd.
    """
    datetime_obj = safe_datetime(purchase_date, "%Y-%m-%d", "purchaseDate")
    return 6 if datetime_obj.day % 2 == 1 else 0


def points_for_purchase_time(purchase_time: str) -> int:
    """
    10 points if the time of purchase is after 2:00pm and before 4:00pm.
    """
    time_obj = safe_datetime(purchase_time, "%H:%M", "purchaseTime").time()
    return 10 if time(14, 0) < time_obj < time(16, 0) else 0
