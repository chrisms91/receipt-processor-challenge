from uuid import uuid4
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Custom exception handler for validation error to return Bad Request instead of 422
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "detail": "The receipt is invalid.",
                "errors": exc.errors(),
            }
        ),
    )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No receipt found for that ID.",
        )
    return {"points": score}
