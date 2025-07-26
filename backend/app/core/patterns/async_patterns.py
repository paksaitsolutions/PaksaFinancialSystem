"""Standardized async/sync patterns"""
import asyncio
from typing import Any, Callable, TypeVar, Awaitable
from functools import wraps

T = TypeVar('T')

def async_to_sync(async_func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """Convert async function to sync"""
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_func(*args, **kwargs))
    return wrapper

class AsyncService:
    """Base class for async services"""
    
    async def execute(self, operation: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute async operation with error handling"""
        try:
            return await operation(*args, **kwargs)
        except Exception as e:
            raise e