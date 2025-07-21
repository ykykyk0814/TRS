import asyncio
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

# Context variable to track async context explicitly when needed
_async_context: ContextVar[bool] = ContextVar("async_context", default=False)


class UnifiedDatabaseSession:
    """
    Unified database session that automatically detects sync/async context.

    Provides a seamless interface for database operations regardless of
    whether the caller is sync or async.
    """

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize both sync and async engines.

        Args:
            database_url: Database connection URL (e.g., 'postgresql://user:pass@localhost/db')
            echo: Whether to echo SQL statements for debugging
        """
        self.database_url = database_url

        # Sync engine and session
        self.sync_engine = create_engine(
            database_url,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
        )
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine, autocommit=False, autoflush=False
        )

        # Async engine and session (convert postgresql:// to postgresql+asyncpg://)
        async_url = self._convert_to_async_url(database_url)
        self.async_engine = create_async_engine(
            async_url, echo=echo, pool_pre_ping=True, pool_recycle=3600
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )

    def _convert_to_async_url(self, url: str) -> str:
        """Convert sync database URL to async version."""
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://")
        elif url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+aiomysql://")
        else:
            # For other databases, assume the URL is already async-compatible
            return url

    def _is_async_context(self) -> bool:
        """
        Efficiently detect if we're running in an async context.

        Uses fast event loop detection and context variables for performance.

        Returns:
            True if running in async context, False otherwise
        """
        # Fast path: Check if explicitly set via context var
        try:
            context_value = _async_context.get()
            # Explicit context variable overrides event loop detection
            return context_value
        except LookupError:
            pass

        # Fallback: Check for running event loop (very fast)
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    @contextmanager
    def get_session(self):
        """
        Get a sync database session.

        Yields:
            SQLAlchemy Session object
        """
        session = self.sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def get_async_session(self):
        """
        Get an async database session.

        Yields:
            SQLAlchemy AsyncSession object
        """
        session = self.async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def auto_session(self):
        """
        Automatically return appropriate session based on context.

        Returns:
            Context manager for appropriate session type
        """
        if self._is_async_context():
            return self.get_async_session()
        else:
            return self.get_session()

    async def dispose(self):
        """Clean up database connections."""
        await self.async_engine.dispose()
        self.sync_engine.dispose()


# Global instance
_db_session_manager: Optional[UnifiedDatabaseSession] = None


def init_db_session_manager(
    database_url: str, echo: bool = False
) -> UnifiedDatabaseSession:
    """
    Initialize the global database session manager.

    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL statements

    Returns:
        UnifiedDatabaseSession instance
    """
    global _db_session_manager
    _db_session_manager = UnifiedDatabaseSession(database_url, echo)
    return _db_session_manager


def get_db_session_manager() -> UnifiedDatabaseSession:
    """
    Get the global database session manager.

    Returns:
        UnifiedDatabaseSession instance

    Raises:
        RuntimeError: If session manager hasn't been initialized
    """
    global _db_session_manager
    if _db_session_manager is None:
        raise RuntimeError(
            "Database session manager not initialized. Call init_db_session_manager() first."
        )
    return _db_session_manager


# Convenience functions for direct use
@contextmanager
def get_sync_session():
    """Convenience function to get sync session."""
    with get_db_session_manager().get_session() as session:
        yield session


@asynccontextmanager
async def get_async_session():
    """Convenience function to get async session."""
    # Set context variable to help with detection
    previous_context = set_async_context(True)
    try:
        async with get_db_session_manager().get_async_session() as session:
            yield session
    finally:
        set_async_context(previous_context)


def set_async_context(value: bool = True) -> bool:
    """
    Explicitly set async context for edge cases.

    Args:
        value: True for async context, False for sync context, None to not change

    Returns:
        Previous context value that was set before this call
    """
    try:
        previous_value = _async_context.get()
    except LookupError:
        previous_value = False  # Default value when no context is set

    if value is not None:
        _async_context.set(value)
    return previous_value


def get_context_info() -> dict:
    """
    Get current context information for debugging.

    Returns:
        Dictionary with context information
    """
    try:
        explicit_async = _async_context.get()
    except LookupError:
        explicit_async = None

    try:
        has_event_loop = asyncio.get_running_loop() is not None
    except RuntimeError:
        has_event_loop = False

    return {
        "explicit_async_context": explicit_async,
        "has_running_event_loop": has_event_loop,
        "detected_async": explicit_async or has_event_loop,
    }
