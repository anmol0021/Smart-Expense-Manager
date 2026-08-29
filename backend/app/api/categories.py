from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.api.dependencies import get_current_user, get_db
from app.models import Category, CategoryType, User
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    category_type: CategoryType | None = Query(default=None, alias="type"),
    database_session: DatabaseSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[CategoryResponse]:
    query = select(Category).where(Category.is_active.is_(True)).order_by(Category.name)
    if category_type is not None:
        query = query.where(Category.type == category_type)
    return [
        CategoryResponse.model_validate(category) for category in database_session.scalars(query)
    ]
