from abc import ABC, abstractmethod
from typing import List

from tanium.types import Params

__all__ = ("FieldABC",)


class FieldABC(ABC):
    @abstractmethod
    def set_field_name(self, field_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_field_name(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_sensor_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_params(self) -> List[Params] | None:
        raise NotImplementedError

    @abstractmethod
    def get_max_age_seconds(self) -> int | None:
        raise NotImplementedError

    @abstractmethod
    def get_many(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_graphql_text(self) -> str:
        raise NotImplementedError
