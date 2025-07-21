import functools
from contextlib import asynccontextmanager, contextmanager
from typing import Awaitable, Callable, Optional, TypeVar

from .session import set_async_context

T = TypeVar("T")


@contextmanager
def force_sync_context():
    """
    Force sync context for the duration of the context manager.

    Useful when you need to ensure sync behavior even in async environment.

    Usage:
        with force_sync_context():
            service.get_data()  # Will use sync session
    """
    previous_context = set_async_context(False)
    try:
        yield
    finally:
        set_async_context(previous_context)


@asynccontextmanager
async def force_async_context():
    """
    Force async context for the duration of the context manager.

    Useful when automatic detection fails.

    Usage:
        async with force_async_context():
            await service.get_data()  # Will use async session
    """
    previous_context = set_async_context(True)
    try:
        yield
    finally:
        set_async_context(previous_context)


def async_context(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorator to explicitly mark a function as async context.

    This ensures that any database operations within this function
    will use async sessions.

    Usage:
        @async_context
        async def my_async_function():
            service = UserService()
            return await service.get_user(1)
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        previous_context = set_async_context(True)
        try:
            return await func(*args, **kwargs)
        finally:
            set_async_context(previous_context)

    return wrapper


def sync_context(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to explicitly mark a function as sync context.

    This ensures that any database operations within this function
    will use sync sessions.

    Usage:
        @sync_context
        def my_sync_function():
            service = UserService()
            return service.get_user(1)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        previous_context = set_async_context(False)
        try:
            return func(*args, **kwargs)
        finally:
            set_async_context(previous_context)

    return wrapper


class SmartContext:
    """
    Smart context manager that automatically handles sync/async context.

    Provides explicit control when needed while maintaining clean API.
    """

    def __init__(self, force_async: Optional[bool] = None):
        """
        Initialize smart context.

        Args:
            force_async: True to force async, False to force sync, None for auto-detect
        """
        self.force_async = force_async

    def __enter__(self):
        """Sync context manager entry."""
        if self.force_async is not None:
            self._previous_context = set_async_context(self.force_async)
        else:
            self._previous_context = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        if self._previous_context is not None:
            set_async_context(self._previous_context)

    async def __aenter__(self):
        """Async context manager entry."""
        if self.force_async is not None:
            self._previous_context = set_async_context(self.force_async)
        else:
            self._previous_context = None
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._previous_context is not None:
            set_async_context(self._previous_context)
