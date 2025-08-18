from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Any, Callable, Dict, Optional, Type, Union

from .exceptions import (
    BaseAPIException,
    handle_api_exception,
    handle_validation_error,
    handle_http_exception,
    handle_generic_exception,
)

def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    # Register our custom exceptions
    app.add_exception_handler(BaseAPIException, handle_api_exception)
    
    # Register standard FastAPI/Starlette exceptions
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(404, handle_http_exception)
    app.add_exception_handler(401, handle_http_exception)
    app.add_exception_handler(403, handle_http_exception)
    app.add_exception_handler(405, handle_http_exception)
    app.add_exception_handler(429, handle_http_exception)
    
    # Register generic exception handler (should be last)
    app.add_exception_handler(Exception, handle_generic_exception)
