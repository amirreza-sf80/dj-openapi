from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Literal

# NOTE: technically, these are frozen classes, but since the code using them is limited,
# and since these are internal API, and doing frozen=True has a performance penalty (albeit small),
# i don't see a reason to make it explicitly frozen
type STATUS_CODE = int | Literal["default"]
type MODEL = type
type METHOD = Literal[
    "get", "post", "patch", "put", "delete", "query", "head", "options", "trace"
]


# ------------------- information about endpoints ---------------------------
@dataclass
class DecoratorFields:
    qs: dict[str, type] | None = None
    request_body: Iterable[MODEL] | MODEL | None = None
    response: dict[STATUS_CODE, Iterable[MODEL] | MODEL] | None = None
    form_body: Iterable[MODEL] | MODEL | None = None
    tags: Sequence[str] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class Metadata:
    """data that is set on views by decorators"""

    method: METHOD
    qs: dict[str, type] | None
    request: Iterable[MODEL] | MODEL | None
    response: dict[STATUS_CODE, Iterable[MODEL] | MODEL] | None
    form: Iterable[MODEL] | MODEL | None
    tags: Sequence[str] = field(default_factory=list)


@dataclass(unsafe_hash=True)
class API:
    """data constructed after extracting info from views"""

    view: Callable
    url: str
    name: str | None
    metadata: Iterable[Metadata]


# ----------------------- openapi --------------------------------

type AnySchema = Schema | ArraySchema | OneOfSchema


@dataclass
class Reference:
    ref: str


@dataclass
class Schema:
    """The generic schema base class.

    Consider using a specialized version (like `IntegerSchema`) instead.
    """

    @unique
    class Type(Enum):
        OBJECT = "object"
        STRING = "string"
        INTEGER = "integer"
        NUMBER = "number"
        BOOLEAN = "boolean"
        NULL = "null"
        ARRAY = "array"

    type: Type | None = None
    properties: dict[str, AnySchema | Reference] | None = None
    format: str | None = None
    additionalProperties: bool | AnySchema | Reference = False
    enum: list[str] | None = None
    required: list[str] = field(default_factory=list)


@dataclass
class ArraySchema:
    items: Reference | AnySchema
    type: Literal[Schema.Type.ARRAY] = Schema.Type.ARRAY


@dataclass
class OneOfSchema:
    oneOf: Sequence[AnySchema | Reference]


@dataclass
class MediaType:
    schema: AnySchema | Reference


# MediaTypeNames are like `application/json`.
type MediaTypeName = str
# HTTP status codes
type StatusCodeType = str


def get_http_response_description(stat: int | Literal["default"]) -> str:
    responses = {
        # 100s, to be complete :)
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        103: "Early Hints",
        # 200s
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        # 300s, to be complete still
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        # 400s
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Content Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        421: "Misdirected Request",
        422: "Unprocessable Content",
        423: "Locked",
        424: "Failed Dependency",
        425: "Too Early",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        # 500s, just in case someone wants to be extra detailed
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        509: "Not Extended",
        511: "Network Authentication Required",
        "default": "the default response",
    }
    return responses[stat]


@dataclass
class Response:
    description: str
    content: dict[MediaTypeName, MediaType] = field(default_factory=dict)


@dataclass
class Parameter:
    @unique
    class Kind(str, Enum):
        QUERY = "query"
        HEADER = "header"
        PATH = "path"
        COOKIE = "cookie"

    name: str
    kind: Kind
    required: bool = False
    schema: AnySchema | Reference | None = None


@dataclass
class RequestBody:
    content: Mapping[MediaTypeName, MediaType]
    description: str | None = None
    required: bool = False


# TODO: all three securitySchemes need custom handling of dataclasses.asdict
# so the field names that don't match the openAPI names are fixed


@dataclass
class ApiKeySecurityScheme:
    name: str
    in_: Literal["query", "header", "cookie"]  # (in)
    description: str | None = None
    type: Literal["apiKey"] = "apiKey"


@dataclass
class HttpSecurityScheme:
    scheme: Literal["basic", "bearer"]
    bearer_format: str | None = None  # only if scheme is bearer (bearerFormat)
    type: Literal["http"] = "http"


@dataclass
class OpenIdSecurityScheme:
    open_id_connect_url: str  # (openIdConnectUrl)
    type: Literal["openIdConnect"] = "openIdConnect"


@dataclass
class Info:
    title: str
    version: str


@dataclass
class Components:
    schemas: dict[str, AnySchema | Reference]
    security_schemes: Mapping[str, ApiKeySecurityScheme] = field(default_factory=dict)


@dataclass
class Operation:
    responses: dict[StatusCodeType, Response]
    parameters: list[Parameter] = field(default_factory=list)
    request_body: RequestBody | None = None
    summary: str | None = None
    tags: Sequence[str] = field(default_factory=list)
    operationId: str | None = None
    description: str | None = None


@dataclass
class PathItem:
    get: Operation | None = None
    post: Operation | None = None
    put: Operation | None = None
    patch: Operation | None = None
    delete: Operation | None = None
    query: Operation | None = None
    head: Operation | None = None
    options: Operation | None = None
    trace: Operation | None = None


type URL = str


@dataclass
class OpenAPI:
    openapi: str
    info: Info
    paths: dict[URL, PathItem]
    components: Components
