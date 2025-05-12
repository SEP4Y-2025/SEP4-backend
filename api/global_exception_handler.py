from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(f"Unhandled exception: {exc}")

    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": str(exc.detail)}
        )

    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": str(exc)}
        )

    elif isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)}
        )

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error: " + str(exc)}
    )
