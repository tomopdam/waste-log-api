from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError, OperationalError

from app.exception_handlers import (
    db_data_error_handler,
    db_integrity_error_handler,
    db_operational_error_handler,
)
from app.exceptions import BaseAppException
from app.routers import register_routers, router

app = FastAPI(
    title="Waste Management Logging API",
    description="Example package for a containerised waste management logging API using FastAPI, SQLModel, PostgreSQL, and nginx.",
    version="0.1.0",
)

# init the db hooks e.g. add automatic updated_at to before_update trigger
from app.db import events as _events

register_routers()
app.include_router(router)

app.add_exception_handler(IntegrityError, db_integrity_error_handler)
app.add_exception_handler(OperationalError, db_operational_error_handler)
app.add_exception_handler(DataError, db_data_error_handler)


@app.exception_handler(BaseAppException)
async def base_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.get("/")
async def main():
    return {
        "message": f"Welcome to Zombocom. This is Zombocom. Welcome. You can do anything at Zombocom. Anything at all! The only limit is yourself.",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy"},
    )
