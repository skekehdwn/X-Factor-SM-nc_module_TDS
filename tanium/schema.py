from typing import Any, Generator

from tanium.abc.schema import SchemaABC
from tanium.fields import Field

__all__ = (
    "Schema",
    "SensorSchema",
    "NodeSchema",
)


def _schema_to_text(schema: "Schema") -> str:
    fields = []
    for field in schema.get_fields():
        if isinstance(field, Schema):
            fields.append(_schema_to_text(field))
            continue
        fields.append(field.get_sensor_name())
    return f'{schema.get_sensor_name()} {{{" ".join(fields)}}}'


class Schema(Field, SchemaABC):
    def get_fields_name(self) -> Generator[str, Any, None]:
        for _field_name in self._meta.fields:
            yield _field_name

    def get_fields(self):
        data = []
        for _field_name in self.get_fields_name():
            _field = getattr(self, _field_name)
            if isinstance(_field, Field):
                _field.set_field_name(_field_name)
                data.append(_field)
        return data


class SensorSchema(Schema):
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

        columns = []
        for field in self.get_fields():
            columns.append(f'"{field.get_sensor_name()}"')
        sensor_columns_text = ",".join(columns)
        graphql_text.append(f"columns: [{sensor_columns_text}]")

        return f'{{{",".join(graphql_text)}}}'


class NodeSchema(Schema):
    def get_graphql_text(self) -> str:
        return _schema_to_text(self)
