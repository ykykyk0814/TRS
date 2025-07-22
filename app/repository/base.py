from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

from app.db.session import get_db_session_manager

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._db_manager = None

    @property
    def db_manager(self):
        """Lazy initialization of database session manager."""
        if self._db_manager is None:
            self._db_manager = get_db_session_manager()
        return self._db_manager

    async def get(self, id: Union[int, UUID]) -> Optional[ModelType]:
        """Get a single record by ID."""
        async with self.db_manager.get_async_session() as session:
            result = await session.get(self.model, id)
            if result:
                # Detach from session to prevent lazy loading issues
                session.expunge(result)
            return result

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination."""
        async with self.db_manager.get_async_session() as session:
            query = select(self.model).offset(skip).limit(limit)
            result = await session.execute(query)
            entities = result.scalars().all()
            # Detach all entities from session
            for entity in entities:
                session.expunge(entity)
            return entities

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        async with self.db_manager.get_async_session() as session:
            if isinstance(obj_in, dict):
                db_obj = self.model(**obj_in)
            else:
                obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in.__dict__
                db_obj = self.model(**obj_data)
            
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            # Detach from session
            session.expunge(db_obj)
            return db_obj

    async def update(self, id: Union[int, UUID], obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> Optional[ModelType]:
        """Update an existing record."""
        async with self.db_manager.get_async_session() as session:
            db_obj = await session.get(self.model, id)
            if not db_obj:
                return None
            
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in.__dict__
            
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            await session.commit()
            await session.refresh(db_obj)
            # Detach from session
            session.expunge(db_obj)
            return db_obj

    async def delete(self, id: Union[int, UUID]) -> bool:
        """Delete a record by ID."""
        async with self.db_manager.get_async_session() as session:
            db_obj = await session.get(self.model, id)
            if not db_obj:
                return False
            
            await session.delete(db_obj)
            await session.commit()
            return True

    # Helper methods for detaching entities (included for your testing)
    def _detach_entity(self, session, entity: Optional[ModelType]) -> Optional[ModelType]:
        """Detach entity from session to prevent lazy loading issues."""
        if entity is not None:
            session.expunge(entity)
        return entity

    def _detach_entities(self, session, entities: List[ModelType]) -> List[ModelType]:
        """Detach list of entities from session."""
        for entity in entities:
            session.expunge(entity)
        return entities 