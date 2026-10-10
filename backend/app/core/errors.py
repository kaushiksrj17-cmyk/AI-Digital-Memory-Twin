"""Centralized Error Handling and Custom Domain Exceptions."""

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from typing import Dict, Any


class EchoException(Exception):
    """Base exception for all ECHO errors."""
    def __init__(self, message: str, status_code: int = 400, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EthicalBoundaryViolation(EchoException):
    """Raised when an interaction attempts to claim consciousness or fabricate identity."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=f"Ethical Boundary Violation: {message}",
            status_code=422,
            details=details
        )


class UnverifiedMemoryAccessError(EchoException):
    """Raised when attempting to present unsupported inference as factual memory."""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=403)


class ProviderNotConfiguredError(EchoException):
    """Raised when an external AI provider is queried without credentials."""
    def __init__(self, provider_name: str):
        super().__init__(
            message=f"AI Provider '{provider_name}' is not configured. Missing API credentials.",
            status_code=503
        )


def register_error_handlers(app: FastAPI):
    """Register custom exception handlers with FastAPI application."""
    @app.exception_handler(EchoException)
    async def echo_exception_handler(request: Request, exc: EchoException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details
            }
        )
