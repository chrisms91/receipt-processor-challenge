from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List


class Item(BaseModel):
    shortDescription: str = Field(
        ...,
        pattern=r"^[\w\s\-]+$",
        json_schema_extra={
            "description": "The short product description for the item.",
            "example": "Mountain Dew 12PK",
        },
    )
    price: str = Field(
        ...,
        pattern=r"^\d+\.\d{2}$",  # e.g., 6.49,
        json_schema_extra={
            "description": "The price paid for this item.",
            "example": "6.49",
        },
    )


class Receipt(BaseModel):
    retailer: str = Field(
        ...,
        pattern=r"^[\w\s\-&]+$",
        json_schema_extra={
            "description": "The name of the retailer or store the receipt is from.",
            "example": "M&M Corner Market",
        },
    )
    purchaseDate: str = Field(
        ...,
        json_schema_extra={
            "type": "date",
            "description": "The date of the purchase printed on the receipt.",
            "example": "2022-01-01",
        },
    )
    purchaseTime: str = Field(
        ...,
        json_schema_extra={
            "type": "time",
            "description": "The time of the purchase printed on the receipt (24-hour format).",
            "example": "13:01",
        },
    )
    items: List[Item] = Field(
        ...,
        min_length=1,
    )
    total: str = Field(
        ...,
        pattern=r"^\d+\.\d{2}$",
        json_schema_extra={
            "description": "The total amount paid on the receipt.",
            "example": "6.49",
        },
    )

    @field_validator("purchaseDate")
    def validate_purchase_date(cls, v: str) -> str:
        """
        Validates if purchaseDate is in the YYYY-MM-DD format
        """
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("purchaseDate must be in YYYY-MM-DD format")
        return v

    @field_validator("purchaseTime")
    def validate_purchase_time(cls, v: str) -> str:
        """
        Validates if purchaseTime is in the HH:MM (24-hour) format
        """
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("purchaseTime must be in HH:MM 24-hour format")
        return v
