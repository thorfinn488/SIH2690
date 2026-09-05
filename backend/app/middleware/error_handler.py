import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        err_msg = errors[0].get("msg") if errors else "Invalid request format"
        if errors and "loc" in errors[0]:
            field = " -> ".join([str(x) for x in errors[0]["loc"]])
            err_msg = f"{field}: {err_msg}"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": err_msg,
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            400: "VALIDATION_ERROR",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
        }

        # Override code if message contains explicit custom error code string
        error_code = code_map.get(exc.status_code, "INTERNAL_ERROR")
        detail_msg = str(exc.detail)
        if "FILE_TOO_LARGE" in detail_msg:
            error_code = "FILE_TOO_LARGE"
        elif "INVALID_FILE_TYPE" in detail_msg:
            error_code = "INVALID_FILE_TYPE"
        elif "AI_PROCESSING_FAILED" in detail_msg:
            error_code = "AI_PROCESSING_FAILED"
        elif "UNAUTHORIZED" in detail_msg:
            error_code = "UNAUTHORIZED"
        elif "FORBIDDEN" in detail_msg:
            error_code = "FORBIDDEN"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": error_code,
                    "message": detail_msg,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred.",
                },
            },
        )
