"""
Auth models compatibility shim.

Prefer app.models.user.User in current architecture.
"""
from app.models.user import User  # re-export for compatibility
__all__ = ["User"]
