import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette import status
from app.core.request_context import request_id_ctx_var

from app.core.config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # ─────────────────────────────────────────────
        # 1️⃣ Generate Request ID
        # ─────────────────────────────────────────────
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request_id_ctx_var.set(request_id)


        # ─────────────────────────────────────────────
        # 2️⃣ Enforce JSON for body methods only
        # ─────────────────────────────────────────────
        if request.method in {"POST", "PUT", "PATCH"}:
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type:
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "invalid_content_type",
                        "message": "Only application/json supported",
                        "request_id": request_id,
                    },
                )

        # ─────────────────────────────────────────────
        # 3️⃣ Enforce Max Body Size
        # ─────────────────────────────────────────────
        body = await request.body()
        if len(body) > settings.MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "payload_too_large",
                    "message": "Request exceeds maximum allowed size",
                    "request_id": request_id,
                },
            )

        response = await call_next(request)

        # Attach request ID to response header
        response.headers["X-Request-ID"] = request_id

        return response
