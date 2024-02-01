from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, Generic, List, Sequence, TypeVar

from requests import Response

from tanium.abc.field import FieldABC

T = TypeVar("T")


class TaniumObjectABC(ABC, Generic[T]):
    @abstractmethod
    def get_fields_name(self) -> Generator[str, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def get_fields(self) -> Generator[FieldABC, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def get_sensors_name(self) -> Generator[str, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def get_sensors_text(self) -> Generator[str, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def get_column_fields(self) -> Generator[FieldABC, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def to_response_json(self, refresh: bool = False) -> Dict | Sequence[Dict]:
        raise NotImplementedError

    @abstractmethod
    def to_iter(self) -> Generator[T, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def to_list(self) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def to_sql(self) -> str:
        raise NotImplementedError
