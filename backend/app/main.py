from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.exceptions import validation_exception_handler
from app.core.security import SecurityMiddleware
from app.api.v1 import health

configure_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(SecurityMiddleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["health"]
)
