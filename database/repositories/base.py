"""Repository Pattern Base Interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Generic repository abstraction for persistence layer."""

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 50) -> List[T]:
        pass

    @abstractmethod
    async def create(self, item: T) -> T:
        pass

    @abstractmethod
    async def update(self, id: str, item_data: dict) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
