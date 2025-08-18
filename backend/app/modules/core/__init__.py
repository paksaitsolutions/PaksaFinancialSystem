"""
Core module containing shared utilities, base classes, and common functionality
used across all other modules in the application.
"""
from .config import settings
from .database import Base, SessionLocal, engine
from .exceptions import (
    AppException,
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
    ServiceUnavailableException,
)
from .security import (
    get_current_user,
    create_access_token,
    verify_password,
    get_password_hash,
    oauth2_scheme,
)
from .logger import setup_logging

# Initialize logging
setup_logging()

__all__ = [
    'settings',
    'Base',
    'SessionLocal',
    'engine',
    'AppException',
    'BadRequestException',
    'NotFoundException',
    'UnauthorizedException',
    'ForbiddenException',
    'ValidationException',
    'ConflictException',
    'ServiceUnavailableException',
    'get_current_user',
    'create_access_token',
    'verify_password',
    'get_password_hash',
    'oauth2_scheme',
]
