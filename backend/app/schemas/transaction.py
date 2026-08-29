from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category_id: UUID
    description: str | None = Field(default=None, max_length=255)
    transaction_date: date

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        return normalized_value or None

    @field_validator("transaction_date")
    @classmethod
    def reject_future_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return value


class TransactionUpdate(BaseModel):
    type: TransactionType | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category_id: UUID | None = None
    description: str | None = Field(default=None, max_length=255)
    transaction_date: date | None = None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        return normalized_value or None

    @field_validator("transaction_date")
    @classmethod
    def reject_future_date(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return value


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category_id: UUID
    type: TransactionType
    amount: Decimal
    description: str | None
    transaction_date: date


class TransactionSort(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    HIGHEST_AMOUNT = "highest_amount"
    LOWEST_AMOUNT = "lowest_amount"


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
