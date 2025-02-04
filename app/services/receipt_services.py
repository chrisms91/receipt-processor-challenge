import math
from uuid import uuid4
from datetime import datetime, time
from fastapi import status
from starlette.exceptions import HTTPException
from app.models.receipt import Receipt
from app.utills import safe_float, safe_datetime

# in-memory store mapping receipt_id to its computed score
receipt_score_store = {}


def process_receipt(receipt: Receipt) -> str:
    """
    Process receipt and calculate its score
    storing the score in the memory, and returning the receipt_id generated
    """
    receipt_id = str(uuid4())
    score = calculate_score(receipt)
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

    # 1 point for every alaphanumeric chars in the retailer name
    for char in receipt.retailer:
        if char.isalnum():
            total_points += 1

    # 50 points if the total price is a round dollar amount with no cents
    if receipt.total.endswith(".00"):
        total_points += 50

    # 25 points if the total is a multiple of 0.25

    total_float = safe_float(receipt.total, "total")
    if total_float % 0.25 == 0:
        total_points += 25

    # 5 points for every two items on the receipt.
    num_pairs = len(receipt.items) // 2
    total_points += num_pairs * 5

    # For each itme: if the trimmed description length is a multiple of 3,
    # multiply the price by 0.2 and round up to the nearest integer, then add that many points.
    # I'm not sure what trimmed means exactly, but I assume it refers to removing leading and trailing whitespaces based on the example provided
    for item in receipt.items:
        short_desc = item.shortDescription.strip()
        if len(short_desc) % 3 == 0:
            price = safe_float(item.price, "price for item")
            points_from_item = math.ceil(price * 0.2)
            total_points += points_from_item

    # 6 points if the day in the purchase date is odd
    purchase_date = safe_datetime(receipt.purchaseDate, "%Y-%m-%d", "purchaseDate")
    if purchase_date.day % 2 == 1:
        total_points += 6

    # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    # Assuming "after" and "before" do not include 2:00 PM and 4:00 PM.

    # purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    purchase_time = safe_datetime(receipt.purchaseTime, "%H:%M", "purchaseTime").time()
    if time(14, 0) < purchase_time < time(16, 0):
        total_points += 10

    return total_points
