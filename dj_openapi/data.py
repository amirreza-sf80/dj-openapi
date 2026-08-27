from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Literal

type STATUS_CODE = int
type MODEL = type


# NOTE: technically, these are frozen classes, but since the code using them is limited,
# and since these are internal API, and doing frozen=True has a performance penalty (albeit small),
# i don't see a reason to make it explicitly frozen
@dataclass(unsafe_hash=True)
class Metadata:
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE", "QUERY", "HEAD", "OPTIONS"]
    qs: Iterable[dict[str, type]] | None
    tags: Iterable[str] | None
    request: Iterable[MODEL] | None
    response: dict[STATUS_CODE, MODEL | Iterable[MODEL]] | None
    form: Iterable[MODEL] | None


@dataclass(unsafe_hash=True)
class API:
    view: Callable
    url: str
    name: str | None
    metadata: Iterable[Metadata]


@dataclass
class Info:
    title: str
    version: str


@dataclass
class Components:
    schemas: dict[str, AnySchema | Reference]
    securitySchemes: Mapping[str, ApiKeySecurityScheme] = Factory(dict)


@dataclass
class Operation:
    responses: dict[StatusCodeType, Response]
    parameters: list[Parameter] = Factory(list)
    requestBody: RequestBody | None = None
    summary: str | None = None
    tags: list[str] = Factory(list)
    operationId: str | None = None
    description: str | None = None


@dataclass
class PathItem:
    get: Operation | None = None
    post: Operation | None = None
    put: Operation | None = None
    patch: Operation | None = None
    delete: Operation | None = None


type URL = str


@dataclass
class OpenAPI:
    openapi: str
    info: Info
    paths: dict[URL, PathItem]
    components: Components
