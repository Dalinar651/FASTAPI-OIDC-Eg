import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger("app.errors")


def _error_payload(*, code: str, message: str, path: str, details: object | None = None) -> dict:
    payload = {
        "error": {
            "code": code,
            "message": message,
            "path": path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


def _request_context(request: Request) -> dict:
    return {
        "method": request.method,
        "path": str(request.url.path),
        "query": str(request.url.query),
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        context = _request_context(request)
        logger.warning(
            "HTTP exception encountered",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                **context,
            },
        )

        details = exc.detail if isinstance(exc.detail, dict | list) else None
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                code="http_error",
                message=message,
                path=context["path"],
                details=details,
            ),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        context = _request_context(request)
        logger.info(
            "Request validation failed",
            extra={
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "errors": exc.errors(),
                **context,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(
                code="validation_error",
                message="Validation failed",
                path=context["path"],
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        context = _request_context(request)
        logger.exception(
            "Unhandled exception encountered",
            extra={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                **context,
            },
            exc_info=exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                code="internal_server_error",
                message="An unexpected error occurred",
                path=context["path"],
            ),
        )
