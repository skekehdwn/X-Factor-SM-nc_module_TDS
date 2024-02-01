from dataclasses import dataclass, field
from typing import Any, Dict, List, TypedDict

__all__ = (
    "Params",
    "Meta",
    "Pagination",
)


class Params(TypedDict):
    name: str
    value: str


class Pagination:
    size: int = 1000


@dataclass
class Meta:
    source_ts: Dict[str, Any] | None = None
    question_name: str | None = None
    fields: List[str] = field(default_factory=list)
    pagination: Pagination = Pagination()
