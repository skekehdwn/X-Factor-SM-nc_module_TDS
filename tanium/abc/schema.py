from abc import ABC, abstractmethod
from typing import Any, Generator

from tanium.abc.field import FieldABC
from tanium.types import Meta


class SchemaABC(FieldABC):
    _meta: Meta = Meta()

    @abstractmethod
    def get_fields_name(self) -> Generator[str, Any, None]:
        raise NotImplementedError

    @abstractmethod
    def get_fields(self) -> Generator[FieldABC, Any, None]:
        raise NotImplementedError
