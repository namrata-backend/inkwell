import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("inkwell")


class InkwellException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(InkwellException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
        )


class ForbiddenException(InkwellException):
    def __init__(self) -> None:
        super().__init__(
            code="FORBIDDEN",
            message="You do not have permission to perform this action",
            status_code=403,
        )


class UnauthorizedException(InkwellException):
    def __init__(self) -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message="Authentication required",
            status_code=401,
        )


class ConflictException(InkwellException):
    def __init__(self, message: str) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
        )


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InkwellException)
    async def inkwell_exception_handler(
        request: Request, exc: InkwellException
    ) -> JSONResponse:
        logger.warning(
            "Application exception",
            extra={"code": exc.code, "status_code": exc.status_code},
        )
        return error_response(exc.code, exc.message, exc.status_code)

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error("Unhandled exception", exc_info=True)
        return error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=500,
        )
