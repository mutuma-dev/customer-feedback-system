

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised by services when something does not exist."""


def register_error_handlers(app: FastAPI) -> None:
    """Teach the app how to turn NotFoundError into a proper HTTP response."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        # The frontend receives {"detail": "Alert not found"} with status 404.
        return JSONResponse(status_code=404, content={"detail": str(exc)})
