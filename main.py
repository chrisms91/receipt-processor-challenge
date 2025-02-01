from uuid import uuid4
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException
from models import Receipt
from service import process_receipt, get_score

app = FastAPI()

"""

POST /receipts/process
    - payload: Receipt Json
    - response: Json containing an id for the receipt
        ex) {"id": "7fb1377b-b223-49d9-a31a-5a02701dd310"}

GET /receipts/:id/points
    - response: Json containing the number of points awarded
        ex) {"points": 32}

"""


@app.get("/")
def root():
    return {
        "message": "Welcome to the receipt-processor API. Please visit /docs page for more details."
    }


@app.post("/receipts/process")
def process_receipt_endpoint(receipt: Receipt):
    """
    Submits a receipt for processing.
    """
    receipt_id = process_receipt(receipt)
    return {"id": receipt_id}


@app.get("/receipts/{id}/points")
async def get_receipt_points_endpoint(id: str):
    """
    Returns the points awarded for the receipt.
    """
    score = get_score(id)
    if not score:
        raise HTTPException(status_code=404, detail="No receipt found for that ID.")
    return {"points": score}
