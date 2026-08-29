from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BudgetStatus(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXCEEDED = "EXCEEDED"


class BudgetCreate(BaseModel):
    category_id: UUID
    month: date
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @field_validator("month")
    @classmethod
    def require_first_day_of_month(cls, value: date) -> date:
        if value.day != 1:
            raise ValueError("Budget month must be the first day of the month")
        return value


class BudgetUpdate(BaseModel):
    category_id: UUID | None = None
    month: date | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)

    @field_validator("month")
    @classmethod
    def require_first_day_of_month(cls, value: date | None) -> date | None:
        if value is not None and value.day != 1:
            raise ValueError("Budget month must be the first day of the month")
        return value


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category_id: UUID
    month: date
    amount: Decimal
    spent: Decimal
    remaining: Decimal
    utilization: Decimal
    status: BudgetStatus
