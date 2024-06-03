from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class Paginated(BaseModel, Generic[T]):
    max: int
    size: int
    count: int
    results: list[T]
