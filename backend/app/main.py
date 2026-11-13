import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import config
from app.database import create_tables
from app.errors import AppError
from app.routers import locations, records, weather

logger = logging.getLogger("weatherlog")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="WeatherLog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(locations.router)
app.include_router(weather.router)
app.include_router(records.router)


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


@app.get("/api/health", tags=["health"])
def health():
    return {"data": {"status": "ok"}}


@app.exception_handler(AppError)
async def handle_app_error(_request: Request, error: AppError):
    return error_response(error.status_code, error.code, error.message)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_request: Request, error: RequestValidationError):
    messages = []
    for item in error.errors():
        field = ".".join(str(part) for part in item["loc"] if part not in ("query", "body", "path"))
        messages.append(f"{field}: {item['msg']}" if field else item["msg"])
    return error_response(422, "validation_error", "; ".join(messages))


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(_request: Request, error: StarletteHTTPException):
    code = "not_found" if error.status_code == 404 else "http_error"
    return error_response(error.status_code, code, str(error.detail))


@app.exception_handler(Exception)
async def handle_unexpected_error(_request: Request, error: Exception):
    logger.exception("Unhandled error", exc_info=error)
    return error_response(500, "internal_error", "Something went wrong on the server.")
