"""Shared exception + handler (Spring equivalent: @ResponseStatus / @ControllerAdvice)."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised by services when something does not exist; turned into HTTP 404."""


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
