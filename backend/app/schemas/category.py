from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.category import CategoryType


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: CategoryType
    is_active: bool
