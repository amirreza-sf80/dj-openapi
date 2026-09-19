from collections.abc import Callable, Iterable
from typing import Any, Literal, Protocol

from django.urls import URLPattern, URLResolver

from dj_openapi.data import API, MODEL, STATUS_CODE, URL, Components, PathItem, Schema

type PATH_PARAM_PARSER = Callable[[str], tuple[str, list[str]]]
type SUMMARY_TRANSFORMER = Callable[[Callable, str], str | None]
type DESCRIPTION_TRANSFORMER = Callable[[Callable, str], str | None]
type DECORATOR_FIELDS = Literal["qs", "request_body", "response", "form_body", "tags"]

type QUERY_STRING = dict[str, type] | None
type RESPONSE_BODY = dict[STATUS_CODE, MODEL | Iterable[MODEL]] | None
type REQUEST_BODY = MODEL | Iterable[MODEL] | None
type FORM_BODY = MODEL | Iterable[MODEL] | None

type Predicate = Callable[[Any], bool]
type BuildHook = Callable[[Any], Schema]


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
