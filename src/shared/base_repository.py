from typing import List, Optional, TypeVar, Generic, Type, Any, Dict
from src.database.db import db
from sqlalchemy.orm import Query
import uuid

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations"""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID"""
        try:
            return self.model.query.get(uuid.UUID(id))
        except (ValueError, TypeError):
            return None

    def get_all(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all entities with pagination"""
        query = self.model.query
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

    def create(self, **kwargs) -> T:
        """Create a new entity"""
        entity = self.model(**kwargs)
        db.session.add(entity)
        db.session.commit()
        return entity

    def bulk_create(self, list: List[dict]) -> List[T]:
        """
        Bulk creates entities
        """
        objects = [self.model(**data) for data in list]
        db.session.bulk_save_objects(objects)
        db.session.commit()
        return objects

    def update(self, id: str, **kwargs) -> Optional[T]:
        """Update an entity"""
        entity = self.get_by_id(id)
        if entity:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            db.session.commit()
        return entity

    def delete(self, id: str) -> bool:
        """Delete an entity"""
        entity = self.get_by_id(id)
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return True
        return False

    def filter_by(self, **kwargs) -> List[T]:
        """Filter entities by given criteria"""
        return self.model.query.filter_by(**kwargs).all()

    def filter(self, *criterion) -> List[T]:
        """Filter entities by SQLAlchemy expressions"""
        return self.model.query.filter(*criterion).all()

    def count(self, **kwargs) -> int:
        """Count entities matching criteria"""
        query = self.model.query
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.count()

    def exists(self, **kwargs) -> bool:
        """Check if entity exists with given criteria"""
        return self.model.query.filter_by(**kwargs).first() is not None
