from typing import List

from tanium.abc.field import FieldABC
from tanium.types import Params

__all__ = (
    "Field",
    "SensorField",
    "NodeField",
)


def validate_data(value: str | None):
    if value is None:
        return ''
    value = value.strip()
    if not len(value):
        return ''
    if value in [
        "None",
        "No Results",
        "No Results Found",
        "Not Specified",
        "[current result unavailable]",
        "[no results]",
        "Did not receive a mailbox response",
        "ERROR: command is not registered",
        "TSE-Error: Failed to send to sensor child process: timed out",
        "TSE-Error: Sensor evaluation timed out",
    ]:
        return ''
    return value


class Field(FieldABC):
    def __init__(
        self,
        *,
        sensor: str,
        max_age_seconds: int | None = None,
        params: List[Params] | None = None,
        many: bool = False,
    ):
        self.sensor: str = sensor
        self.max_age_seconds: int | None = max_age_seconds
        self.params: List[Params] | None = params
        self.field_name: str | None = None
        self.many: bool = many

    def set_field_name(self, field_name: str) -> None:
        self.field_name: str = field_name

    def get_field_name(self) -> str:
        return self.field_name

    def get_sensor_name(self) -> str:
        return self.sensor

    def get_params(self) -> List[Params] | None:
        return self.params

    def get_max_age_seconds(self) -> int | None:
        return self.max_age_seconds

    def get_many(self) -> bool:
        return self.many

    def get_graphql_text(self) -> str:
        return self.sensor

    def __validate__(self):
        yield validate_data


class SensorField(Field):
    def get_graphql_text(self) -> str:
        graphql_text = [f'name: "{self.sensor}"']
        if self.params is not None:
            sensor_params_text = ",".join(
                map(
                    lambda x: (f'{{name: "{x["name"]}", value: "{x["value"]}"}}'),
                    self.params,
                )
            )
            graphql_text.append(f"params: [{sensor_params_text}]")

        return f'{{{",".join(graphql_text)}}}'


class NodeField(Field):
    pass
