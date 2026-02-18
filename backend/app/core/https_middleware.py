from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class HTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only enforce in production when enabled
        if settings.ENV == "production" and settings.ENFORCE_HTTPS:
            forwarded_proto = request.headers.get("x-forwarded-proto")
            scheme = forwarded_proto or request.url.scheme

            if scheme != "https":
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "HTTPS required"},
                )

        return await call_next(request)
