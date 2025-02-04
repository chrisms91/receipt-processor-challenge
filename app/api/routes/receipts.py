from fastapi import APIRouter, HTTPException, status
from app.models.receipt import Receipt
from app.services.receipt_services import get_score, process_receipt

router = APIRouter()


@router.get("/{id}/points")
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


@router.post("/process")
def process_receipt_endpoint(receipt: Receipt):
    """
    Submits a receipt for processing.
    """
    receipt_id = process_receipt(receipt)
    return {"id": receipt_id}
