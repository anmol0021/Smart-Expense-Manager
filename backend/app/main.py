from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.budgets import router as budgets_router
from app.api.categories import router as categories_router
from app.api.dashboard import router as dashboard_router
from app.api.transactions import router as transactions_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Smart Expense & Budget Manager API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(budgets_router)
app.include_router(categories_router)
app.include_router(dashboard_router)
app.include_router(transactions_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exception: HTTPException) -> JSONResponse:
    error_codes = {
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
    }
    message = exception.detail if isinstance(exception.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": {
                "code": error_codes.get(exception.status_code, "REQUEST_ERROR"),
                "message": message,
            }
        },
        headers=exception.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exception: RequestValidationError
) -> JSONResponse:
    messages = [error["msg"] for error in exception.errors()]
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "; ".join(messages)}},
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
