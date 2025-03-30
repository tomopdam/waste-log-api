from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError, OperationalError


def format_detail(exc: Exception) -> str:
    message = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    if "UNIQUE constraint" in message or "duplicate key" in message:
        return "A record with these details already exists."
    return message


async def db_integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": format_detail(exc)},
    )


async def db_operational_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database is temporarily unavailable. Please try again later."
        },
    )


async def db_data_error_handler(request: Request, exc: DataError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid data format or value."},
    )
