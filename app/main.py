from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from app.api.routes import receipts

app = FastAPI(
    title="Receipt Processor", description="A simple receipt processor", version="1.0.0"
)


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


app.include_router(receipts.router, prefix="/receipts", tags=["receipts"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the receipt-processor API. Please visit /docs page for more details."
    }
