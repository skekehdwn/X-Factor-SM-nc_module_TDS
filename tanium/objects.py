import json
import time
from http import HTTPStatus
from typing import Any, Dict, Generator, Generic, List, Type, TypeVar

import requests
import urllib3
from requests import Response, Session

from tanium.abc.objects import TaniumObjectABC, TaniumQObjectABC
from tanium.env import TANIUM_HOST, TANIUM_PASSWORD, TANIUM_USER
from tanium.fields import Field, NodeField, SensorField
from tanium.schema import NodeSchema, Schema, SensorSchema
from tanium.types import Meta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

T = TypeVar("T")

__all__ = (
    "EndpointTDSObject",
    "EndpointTSObject",
    "TaniumRestObject"
)


def _get_login_token(session: Session) -> str:
    response = session.post(
        f"{TANIUM_HOST}/api/v2/session/login",
        data=json.dumps(
            {
                "username": TANIUM_USER,
                "password": TANIUM_PASSWORD,
                "domain": "",
            }
        ),
        verify=False,
    )
    return response.json()["data"]["session"]


def _set_login_headers(session: Session):
    token = _get_login_token(session)
    session.headers = {
        "session": token,
        "Content-Type": "application/json",
    }


def _field_to_list(data_list: List, n: int):
    values = []
    for data in data_list[n]:
        values.append(data["text"])
    return values


def _schema_to_dict(schema: Schema, data_list: List, n: int):
    m = n
    _value = {}
    for _schema_field in schema.get_fields():
        _value[_schema_field.get_field_name()] = data_list[m][0]["text"]
        m += 1
    _copy_object: CopyObject = CopyObject(**_value)
    return _copy_object


def _schema_to_list(schema: Schema, data_list: List, n: int):
    len_data = len(data_list[n])
    values = []
    for mn in range(len_data):
        m = n
        _value = {}
        for _schema_field in schema.get_fields():
            _value[_schema_field.get_field_name()] = data_list[m][mn]["text"]
            m += 1
        _copy_object: CopyObject = CopyObject(**_value)
        values.append(_copy_object)
    return values


class CopyObject(object):
    def __init__(self, **kwargs):
        self.__values__ = kwargs

    def __getattr__(self, item):
        return self.__values__[item]

    def __repr__(self):
        return self.__values__.__repr__()


class EndpointTDSObject(TaniumObjectABC, Generic[T]):
    def __init__(self, cls: Type[T]):
        self.object: Type[T] = cls
        self.object_meta: Meta = cls._meta
        self.response: Response | None = None

    def get_fields_name(self) -> Generator[str, Any, None]:
        for field_name in self.object_meta.fields:
            yield field_name

    def get_fields(self):
        data = []
        for field_name in self.get_fields_name():
            field = getattr(self.object, field_name)
            if isinstance(field, Field):
                field.set_field_name(field_name)
                data.append(field)
        return data

    def get_sensors_name(self) -> Generator[str, Any, None]:
        for field in self.get_fields():
            yield field.get_sensor_name()

    def get_column_fields(self):
        data = []
        for field in self.get_fields():
            if isinstance(field, Schema):
                for _field in field.get_fields():
                    data.append(_field)
                continue
            data.append(field)
        return data

    def get_sensors_field(
        self,
    ) -> Generator[SensorField | SensorSchema, Any, None]:
        for field in self.get_fields():
            if isinstance(field, SensorField):
                yield field
            elif isinstance(field, SensorSchema):
                yield field

    def get_sensors_text(self) -> Generator[str, Any, None]:
        for field in self.get_sensors_field():
            yield field.get_graphql_text()

    def get_nodes_field(
        self,
    ) -> Generator[NodeField | NodeSchema, Any, None]:
        for field in self.get_fields():
            if isinstance(field, NodeField):
                yield field
            elif isinstance(field, NodeSchema):
                yield field

    def get_nodes_text(self) -> Generator[str, Any, None]:
        for field in self.get_nodes_field():
            yield field.get_graphql_text()

    def get_graphql_text(self):
        _query = " ".join(
            [
                f"query endpoints($after: Cursor, $first: Int)"
                f"{{endpoints(after: $after, first: $first) {{pageInfo",
                f"{{hasNextPage startCursor endCursor}} totalRecords edges"
                f"{{cursor node {{",
                " ".join(self.get_nodes_text()),
                f"sensorReadings(sensors: [",
                " ".join(self.get_sensors_text()),
                f"]) {{columns {{name values}}}}}}}}}}}}",
            ]
        )
        return _query

    def get_graphql_endpoints(
        self,
        session: Session,
        after: str | None = None,
    ) -> Response:
        response = session.post(
            f"{TANIUM_HOST}/plugin/products/gateway/graphql",
            data=json.dumps(
                {
                    "query": self.get_graphql_text(),
                    "variables": {
                        "after": after,
                        "first": self.object_meta.pagination.size,
                    },
                }
            ),
            verify=False,
        )
        return response

    def to_response_json(self, refresh: bool = False) -> List[Dict]:
        has_next_page: bool = True
        cursor: str | None = None
        response_list = []
        with requests.session() as session:
            _set_login_headers(session)
            while has_next_page:
                response = self.get_graphql_endpoints(session, cursor)

                response_json = response.json()
                response_list.append(response_json)
                page_info = response_json["data"]["endpoints"]["pageInfo"]
                has_next_page = page_info["hasNextPage"]
                cursor = page_info["endCursor"]
                print(response_json["data"]["endpoints"]["totalRecords"])
        return response_list

    def _sensor_row_to_object_iter(
        self,
        edge: Dict,
        sensors_field: Generator[Field, Any, None],
        n: int = 0,
        i: int = 0,
    ):
        value = {}
        for m, field in enumerate(sensors_field):
            many = field.get_many()
            if isinstance(field, Schema):
                if many:
                    value[field.get_field_name()] = []
                    len_value = len(edge[n + m]["values"])
                    for j in range(len_value):
                        node_value = self._sensor_row_to_object_iter(
                            edge,
                            field.get_fields(),
                            n + m,
                            j,
                        )
                        value[field.get_field_name()].append(
                            CopyObject(**node_value)
                        )
                else:
                    value[field.get_field_name()] = CopyObject(
                        **self._sensor_row_to_object_iter(
                            edge,
                            field.get_fields(),
                            n + m,
                        )
                    )
                n += len(field.get_fields()) - 1
            else:
                if many:
                    data = edge[n + m]["values"]
                else:
                    data = edge[n + m]["values"][i]
                for validate_func in field.__validate__():
                    data = validate_func(data)
                value[field.get_field_name()] = data
        return value

    def _node_row_to_object_iter(
        self,
        edge: Dict,
        nodes_field: Generator[Field, Any, None],
    ):
        value = {}
        for field in nodes_field:
            many = field.get_many()
            if isinstance(field, Schema):
                if many:
                    value[field.get_field_name()] = []
                    for node in edge[field.get_sensor_name()]:
                        node_value = self._node_row_to_object_iter(
                            node,
                            field.get_fields(),
                        )
                        value[field.get_field_name()].append(
                            CopyObject(**node_value)
                        )
                else:
                    value[field.get_field_name()] = CopyObject(
                        **self._node_row_to_object_iter(
                            edge[field.get_sensor_name()],
                            field.get_fields(),
                        )
                    )
            else:
                value[field.get_field_name()] = edge[field.get_sensor_name()]
        return value

    def to_iter(self) -> Generator[T, Any, None]:
        response_json_list = self.to_response_json()
        for response_json in response_json_list:
            edges = response_json["data"]["endpoints"]["edges"]
            for edge in edges:
                sensors_field = self.get_sensors_field()
                nodes_field = self.get_nodes_field()
                value = {}
                node = edge["node"]
                node_value = self._node_row_to_object_iter(node, nodes_field)
                sensor_value = self._sensor_row_to_object_iter(
                    node["sensorReadings"]["columns"],
                    sensors_field,
                )
                value.update(node_value)
                value.update(sensor_value)
                copy_object: CopyObject = CopyObject(**value)
                yield copy_object

    def to_list(self) -> List[T]:
        response_json_list = self.to_response_json()
        values = []
        for response_json in response_json_list:
            edges = response_json["data"]["endpoints"]["edges"]
            for edge in edges:
                sensors_field = self.get_sensors_field()
                nodes_field = self.get_nodes_field()
                value = {}
                node = edge["node"]
                value.update(self._node_row_to_object_iter(node, nodes_field))
                value.update(
                    self._sensor_row_to_object_iter(
                        node["sensorReadings"]["columns"],
                        sensors_field,
                    )
                )
                copy_object: CopyObject = CopyObject(**value)
                values.append(copy_object)
        return values

    def to_list_value(self):
        response_json_list = self.to_response_json()
        values = []
        for response_json in response_json_list:
            edges = response_json["data"]["endpoints"]["edges"]
            for edge in edges:
                sensors_field = self.get_sensors_field()
                nodes_field = self.get_nodes_field()
                value = {}
                node = edge["node"]
                value.update(self._node_row_to_object_iter(node, nodes_field))
                value.update(
                    self._sensor_row_to_object_iter(
                        node["sensorReadings"]["columns"],
                        sensors_field,
                    )
                )
                copy_object: CopyObject = CopyObject(**value)
                append_value = []
                i = 0
                for n, field in enumerate(self.get_fields()):
                    data = []
                    field_name = field.get_field_name()
                    _field_value = getattr(copy_object, field_name)
                    if isinstance(field, Schema):
                        for m, schema_in_field in enumerate(field.get_fields()):
                            data = []
                            schema_in_field_name = schema_in_field.get_field_name()
                            if isinstance(_field_value, list):
                                for _value in _field_value:
                                    _schema_in_field_value = getattr(_value, schema_in_field_name)
                                    data.append({'text': _schema_in_field_value})
                            else:
                                _schema_in_field_value = getattr(_field_value, schema_in_field_name)
                                data.append({'text': _schema_in_field_value})
                            append_value.append(data)
                        i += m
                    else:
                        data = []
                        if isinstance(_field_value, list):
                            for _value in _field_value:
                                data.append({'text': _value})
                        else:
                            data.append({'text': _field_value})
                        append_value.append(data)
                values.append({
                    'id': 0,
                    'cid': 0,
                    'data': append_value,
                })
        response_format = {
            'data': {
                'result_sets': [
                    {'rows': values}
                ]
            }
        }
        return response_format

    def to_sql(self) -> Generator[str, Any, None]:
        for data in self.to_iter():
            yield self.object.to_sql(data)


class TaniumObject(TaniumQObjectABC, Generic[T]):
    def __init__(self, cls: Type[T]):
        self.object: Type[T] = cls
        self.object_meta: Meta = cls._meta
        self.response: Response | None = None

    def get_fields_name(self) -> Generator[str, Any, None]:
        for field_name in self.object_meta.fields:
            yield field_name

    def get_fields(self) -> Generator[Field, Any, None]:
        for field_name in self.get_fields_name():
            field = getattr(self.object, field_name)
            if isinstance(field, Field):
                field.set_field_name(field_name)
                yield field

    def get_sensors_name(self) -> Generator[str, Any, None]:
        for field in self.get_fields():
            yield field.get_sensor_name()

    def get_sensors_text(self) -> Generator[str, Any, None]:
        for field in self.get_fields():
            yield field.get_question_text()

    def get_column_fields(self) -> Generator[Field, Any, None]:
        for field in self.get_fields():
            if isinstance(field, Schema):
                yield from field.get_fields()
                continue
            yield field

    def to_response_json(self, refresh: bool = False) -> Dict:
        response = self.to_response(refresh=refresh)
        return response.json()


class TaniumRestObject(TaniumObject, Generic[T]):
    def __init__(self, cls: Type[T]):
        super().__init__(cls)

    def get_question_text(self):
        sensors = " and ".join(self.get_sensors_text())
        return f"Get {sensors} from all machines"

    def _create_question_id(self, session: Session) -> int:
        response = session.post(
            f"{TANIUM_HOST}/api/v2/questions",
            data=json.dumps({"query_text": self.get_question_text()}),
            headers = {
                "session": self.token,
                "Content-Type": "application/json",
            },
            verify=False,
        )
        question_id: int = response.json()["data"]["id"]
        return question_id

    def _get_question_result(self, session: Session, question_id: int):
        response = session.post(
            f"{TANIUM_HOST}/api/v2/result_data/question/{question_id}",
            headers = {
                "session": self.token,
                "Content-Type": "application/json",
            },
            verify=False,
        )
        return response

    def _find_saved_question(self, session: Session) -> int | None:
        response = session.get(
            (
                f"{TANIUM_HOST}/api/v2/"
                f"saved_questions/by-name/"
                f"{self.object_meta.question_name}"
            ),
            verify=False,
        )
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None
        return response.json()["data"]["id"]

    def _create_saved_question(
        self,
        session: Session,
        question_id: int,
    ) -> int:
        response = session.post(
            f"{TANIUM_HOST}/api/v2/saved_questions",
            data=json.dumps(
                {
                    "name": self.object_meta.question_name,
                    "question": {"id": question_id},
                }
            ),
            verify=False,
        )
        return response.json()["data"]["id"]

    def _get_saved_question_result(
        self,
        session: Session,
        saved_question_id: int,
    ) -> Response:
        response = session.post(
            (
                f"{TANIUM_HOST}/api/v2/"
                f"result_data/saved_question/{saved_question_id}"
            ),
            verify=False,
        )
        return response

    def _get_question_response(self, session: Session) -> Response:
        question_id = self._create_question_id(session)
        time.sleep(100)
        response = self._get_question_result(session, question_id)
        return response

    def to_response(self, refresh: bool = False) -> Response:
        token = _get_login_token(requests)
        self.token = token
        question_id = self._create_question_id(requests)
        time.sleep(5)
        token = _get_login_token(requests)
        self.token = token
        response = self._get_question_result(requests, question_id)
        return response

    def to_iter(self, refresh: bool = False) -> Generator[T, Any, None]:
        response_json = self.to_response_json(refresh=refresh)
        result = response_json["data"]["result_sets"][0]
        for row in result.get("rows", []):
            value = {}
            n = 0
            for field in self.get_fields():
                many = field.get_many()
                data = row["data"]
                if isinstance(field, Schema):
                    if many:
                        value[field.get_field_name()] = _schema_to_list(
                            field,
                            data,
                            n,
                        )
                    else:
                        value[field.get_field_name()] = _schema_to_dict(
                            field,
                            data,
                            n,
                        )
                    n += len(list(field.get_fields()))
                else:
                    if many:
                        value[field.get_field_name()] = _field_to_list(
                            data,
                            n,
                        )
                    else:
                        value[field.get_field_name()] = data[n][0]["text"]
                    n += 1
            copy_object: CopyObject = CopyObject(**value)
            yield copy_object

    def to_list(self, refresh: bool = False) -> List[T]:
        response_json = self.to_response_json(refresh=refresh)
        result = response_json["data"]["result_sets"][0]
        values = []
        for row in result.get("rows", []):
            value = {}
            n = 0
            for field in self.get_fields():
                many = field.get_many()
                data = row["data"]
                if isinstance(field, Schema):
                    if many:
                        value[field.get_field_name()] = _schema_to_list(
                            field,
                            data,
                            n,
                        )
                    else:
                        value[field.get_field_name()] = _schema_to_dict(
                            field,
                            data,
                            n,
                        )
                    n += len(list(field.get_fields()))
                else:
                    if many:
                        value[field.get_field_name()] = _field_to_list(
                            data,
                            n,
                        )
                    else:
                        value[field.get_field_name()] = data[n][0]["text"]
                    n += 1
            copy_object: CopyObject = CopyObject(**value)
            values.append(copy_object)
        return values



class EndpointTSObject(EndpointTDSObject, Generic[T]):
    def get_graphql_text(self):
        _query = " ".join(
            [
                f"query endpoints($after: Cursor, $first: Int,"
                f"$stableWaitTime: Int, $minPercentage: Float)"
                f"{{endpoints(after: $after, first: $first,"
                f"source:{{ ts: {{ stableWaitTime: $stableWaitTime,"
                f"minPercentage: $minPercentage }} }}) {{pageInfo",
                f"{{hasNextPage startCursor endCursor}}",
                f"collectionInfo {{expectedTotal respondedTotal",
                f"respondedPercentage success}}",
                f"edges {{cursor node {{",
                " ".join(self.get_nodes_text()),
                f"sensorReadings(sensors: [",
                " ".join(self.get_sensors_text()),
                f"]) {{columns {{name values}}}}}}}}}}}}",
            ]
        )
        return _query

    def get_graphql_endpoints(
        self,
        session: Session,
        after: str | None = None,
    ) -> Response:
        response = session.post(
            f"{TANIUM_HOST}/plugin/products/gateway/graphql",
            data=json.dumps(
                {
                    "query": self.get_graphql_text(),
                    "variables": {
                        "after": after,
                        "first": self.object_meta.pagination.size,
                        "stableWaitTime": (
                            self.object_meta.source_ts["stable_wait_time"]
                        ),
                        "minPercentage": (
                            self.object_meta.source_ts["min_percentage"]
                        ),
                    },
                },
            ),
            verify=False,
        )
        return response
