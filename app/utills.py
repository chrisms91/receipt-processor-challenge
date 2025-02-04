from datetime import datetime
from starlette.exceptions import HTTPException


def safe_float(value: str, field_name: str) -> float:
    """
    Converts a string to a float.
    Raises an HTTPException with a 400 status if conversion fails.
    """
    try:
        return float(value)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"The receipt is invalid: Invalid {field_name} value '{value}'",
        )


def safe_datetime(value: str, fmt: str, field_name: str) -> datetime:
    """
    Converts a string to a datetime object using the given format.
    Raises an HTTPException with a 400 status if conversion fails.
    """
    try:
        return datetime.strptime(value, fmt)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"The receipt is invalid: Invalid {field_name} value '{value}'. Expected format: {fmt}",
        )
