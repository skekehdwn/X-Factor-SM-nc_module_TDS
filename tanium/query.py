from typing import Any, Generator, Type

from tanium.objects import EndpointTDSObject, EndpointTSObject, TaniumRestObject
from tanium.types import Meta

__all__ = (
    "QuestionQuery",
    "CacheQuery",
)


class QueryMeta(type):
    def __getattr__(cls, item):
        if item == "objects":
            cls.objects = cls.__objects_cls__(cls)
            return cls.objects


class CacheQuery(metaclass=QueryMeta):
    _meta: Meta = Meta()

    __objects_cls__: Type[EndpointTDSObject] = EndpointTDSObject
    objects: EndpointTDSObject

    def to_sql(self, value) -> Generator[str, Any, None]:
        yield str(value)


class QuestionQuery(metaclass=QueryMeta):
    _meta: Meta = Meta()

    __objects_cls__: Type[TaniumRestObject] = TaniumRestObject
    objects: TaniumRestObject
