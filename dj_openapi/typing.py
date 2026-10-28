from collections.abc import Callable, Iterable
from typing import Any, Literal, Protocol, TypeVar

from django.urls import URLPattern, URLResolver

from dj_openapi.data import (
    API,
    MODEL,
    STATUS_CODE,
    URL,
    AnySchema,
    Components,
    PathItem,
    QueryParam,
)

type PATH_PARAM_PARSER = Callable[[str], tuple[str, list[str], str]]
type SUMMARY_TRANSFORMER = Callable[[Callable, str], str | None]
type DESCRIPTION_TRANSFORMER = Callable[[Callable, str], str | None]
type DECORATOR_FIELDS = Literal[
    "qs", "request_body", "response_body", "form_body", "tags", "content_type"
]

type QUERY_STRING = dict[str, type | QueryParam | Any] | None
type RESPONSE_BODY = dict[STATUS_CODE, MODEL | Iterable[MODEL]] | None
type REQUEST_BODY = MODEL | Iterable[MODEL] | None
type FORM_BODY = MODEL | Iterable[MODEL] | None

type Predicate = Callable[[Any], bool]
type BuildHook = Callable[[Any, bool], AnySchema]


class SchemaProtocol(Protocol):
    path_items: dict[URL, PathItem]
    components: Components

    def __init__(
        self,
        api_patterns: set[API],
        path_param_parser: PATH_PARAM_PARSER,
        summary_reader: SUMMARY_TRANSFORMER,
        description_reader: DESCRIPTION_TRANSFORMER,
    ): ...

    def build(self): ...


type PATTERNS = Iterable[URLPattern | URLResolver]
type DISCOVERER = Callable[[PATTERNS, str, set[str] | None], set[API]]


T = TypeVar("T")


class SerializerProtocol(Protocol):
    def dumps(self, obj: Any, unstructure_as: Any = None, **kwargs: Any): ...
    def loads(self, data: bytes | str, cl: type[T], **kwargs: Any) -> T: ...
    def unstructure(self, obj: Any, unstructure_as: Any = None) -> Any: ...
    def structure(self, obj: Any, cl: type[T]) -> T: ...
