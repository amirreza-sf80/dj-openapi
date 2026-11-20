import types
from collections.abc import Iterable
from dataclasses import _MISSING_TYPE, is_dataclass
from dataclasses import fields as dt_fields
from inspect import signature
from typing import Any, TypeAliasType

from attrs import NOTHING, has
from attrs import fields as at_fields
from cattrs._compat import (
    get_args,
    is_annotated,
    is_generic,
    is_literal,
    is_tuple,
    is_union_type,
)
from cattrs.cols import is_mapping, is_sequence
from django.core.files.uploadedfile import UploadedFile

from dj_openapi.base_schema_builder import (
    PYTHON_PRIMITIVES_TO_OPENAPI,
    STR_TO_PYTHON,
    BaseSchemaBuilder,
)
from dj_openapi.data import (
    API,
    METHOD,
    URL,
    AnySchema,
    ApiKey,
    ApiKeySecurityScheme,
    ArraySchema,
    BoolSchema,
    BytesSchema,
    Components,
    DateSchema,
    DateTimeSchema,
    DoubleSchema,
    Http,
    HttpSecurityScheme,
    IntSchema,
    MediaType,
    Metadata,
    NullSchema,
    OAuth2,
    OAuth2SecurityScheme,
    OAuth2SecuritySchemeFlows,
    OneOfSchema,
    OpenId,
    OpenIdSecurityScheme,
    Operation,
    Parameter,
    PathItem,
    QueryParam,
    Reference,
    RequestBody,
    Response,
    Schema,
    SecurityScheme,
    StatusCodeType,
    StrSchema,
    TimeSchema,
    get_http_response_description,
)
from dj_openapi.typing import (
    DESCRIPTION_TRANSFORMER,
    PATH_PARAM_PARSER,
    SUMMARY_TRANSFORMER,
    BuildHook,
    Predicate,
)

try:
    from msgspec import Struct
    from msgspec.inspect import (
        NODEFAULT,
        AnyType,
        BoolType,
        BytesType,
        DataclassType,
        DateTimeType,
        DateType,
        DecimalType,
        DictType,
        Field,
        FloatType,
        IntType,
        ListType,
        LiteralType,
        NoneType,
        StrType,
        StructType,
        TimeType,
        TupleType,
        Type,
        UnionType,
        VarTupleType,
        type_info,
    )

    MSGSPEC_PRIMITIVES_TO_OPENAPI: dict[type, type[Schema]] = {
        AnyType: Schema,
        StrType: StrSchema,
        IntType: IntSchema,
        BoolType: BoolSchema,
        FloatType: DoubleSchema,
        DecimalType: DoubleSchema,
        BytesType: BytesSchema,
        DateType: DateSchema,
        DateTimeType: DateTimeSchema,
        TimeType: TimeSchema,
        NoneType: NullSchema,
    }

    has_msgspec = True
except ImportError:
    has_msgspec = False

    class Struct:
        pass

    class Type:
        pass

    NODEFAULT = object()


def is_file(type):
    if is_annotated(type):
        type = get_args(type)[0]
    return isinstance(type, UploadedFile)


class SchemaBuilder(BaseSchemaBuilder):
    def __init__(
        self,
        api_patterns: list[API],
        path_param_parser: PATH_PARAM_PARSER,
        summary_reader: SUMMARY_TRANSFORMER,
        description_reader: DESCRIPTION_TRANSFORMER,
    ):
        self.build_rules: list[tuple[Predicate, BuildHook]] = self.default_build_rules()
        self.api_patterns = api_patterns
        self.path_param_parser = path_param_parser
        self.summary_reader = summary_reader
        self.description_reader = description_reader
        self.names: dict[tuple[type, bool], str] = {}
        self._components: dict[str, AnySchema | Reference] = {}
        self._security_components: dict[str, SecurityScheme] = {}
        self.path_items: dict[URL, PathItem] = {}
        self.generic_mapping = {}
        self._has_file = False

    @property
    def components(self) -> Components:
        return Components(self._components, self._security_components)

    def build(self):
        for api in self.api_patterns:
            item: dict[METHOD, Operation] = {}
            for metadata in api.metadata:
                item[metadata.method] = self.build_operation(
                    api,
                    metadata,
                    self.path_param_parser,
                    self.summary_reader,
                    self.description_reader,
                )
            url = self.path_param_parser(api.url)[0] if api.url else "/"
            if not url.startswith("/"):
                url = f"/{url}"
            self.path_items[url] = PathItem(**item)

    def build_operation(
        self,
        api: API,
        metadata: Metadata,
        path_param_parser: PATH_PARAM_PARSER,
        summary_reader,
        description_reader,
    ) -> Operation:
        request_bodies = {}
        resps: dict[StatusCodeType, Response] = {"200": Response(description="OK")}
        params: list[Parameter] = []
        security = None
        sig = signature(api.view, eval_str=True)
        path = path_param_parser(api.url)
        path_params = path[1]

        # path parameters
        for path_param in path_params:
            if path_param not in sig.parameters:
                raise ValueError(f"Path parameter {path_param} not found")
            t = STR_TO_PYTHON.get(path[2], types.NoneType)
            params.append(
                Parameter(
                    path_param,
                    Parameter.Kind.PATH,
                    True,
                    schema=PYTHON_PRIMITIVES_TO_OPENAPI[t](),
                )
            )

        # request bodies
        self._has_file = False
        if metadata.request:
            if not isinstance(metadata.request, Iterable):
                media = MediaType(self.get_schema_for_type(metadata.request))
                content_type = (
                    "multipart/form-data" if self._has_file else metadata.content_type
                )
                if self._has_file or isinstance(content_type, str):
                    request_bodies[content_type] = media
                else:
                    for c in content_type:
                        request_bodies[c] = media
            else:
                media = MediaType(
                    OneOfSchema([self.get_schema_for_type(r) for r in metadata.request])
                )
                content_type = (
                    "multipart/form-data" if self._has_file else metadata.content_type
                )
                if self._has_file or isinstance(content_type, str):
                    request_bodies[content_type] = media
                else:
                    for c in content_type:
                        request_bodies[c] = media
            self._has_file = False

        # request forms
        if metadata.form:
            if not isinstance(metadata.form, Iterable):
                media = MediaType(self.get_schema_for_type(metadata.form))
                content_type = (
                    "multipart/form-data"
                    if self._has_file
                    else "application/x-www-form-urlencoded"
                )
                request_bodies[content_type] = media
            else:
                media = MediaType(
                    OneOfSchema([self.get_schema_for_type(r) for r in metadata.form])
                )
                content_type = (
                    "multipart/form-data"
                    if self._has_file
                    else "application/x-www-form-urlencoded"
                )
                request_bodies[content_type] = media
            self._has_file = False

        req_body = None
        if request_bodies:
            req_body = RequestBody(request_bodies, required=True)

        # query strings
        if metadata.qs:
            for q, t in metadata.qs.items():
                if isinstance(t, QueryParam):
                    req = t.required
                    ty = self.get_schema_for_type(t.type)
                    des = t.description
                else:
                    req = False
                    ty = self.get_schema_for_type(t)
                    des = None
                params.append(Parameter(q, Parameter.Kind.QUERY, req, des, ty))

        # response
        self._has_file = False
        if metadata.response:
            for stat, res in metadata.response.items():
                if not isinstance(res, Iterable):
                    r = MediaType(self.get_schema_for_type(res, is_response=True))
                elif res:
                    r = MediaType(
                        OneOfSchema(
                            [self.get_schema_for_type(r, is_response=True) for r in res]
                        )
                    )
                else:
                    r = None

                desc = get_http_response_description(stat)
                if isinstance(stat, int) and (stat < 200 or stat == 204 or stat == 304):
                    resp = Response(desc)
                else:
                    if isinstance(metadata.content_type, str):
                        resp = Response(
                            desc, content={metadata.content_type: r} if r else {}
                        )
                    else:
                        resp = Response(
                            desc,
                            content={c: r for c in metadata.content_type} if r else {},
                        )

                resps[str(stat)] = resp

        if metadata.security:
            sec = metadata.security
            if isinstance(sec, (OpenId, OAuth2)):
                scope = sec.scopes
            else:
                scope = []
            security = [{sec.name: scope}]
            self._security_components[sec.name] = self.build_security_component(sec)

        return Operation(
            resps,
            params,
            requestBody=req_body,
            summary=summary_reader(api.view, api.name),
            tags=metadata.tags,
            operationId=api.name,
            description=description_reader(api.view, api.name),
            security=security,
        )

    def get_schema_for_type(
        self, type: Any, is_response=False
    ) -> Reference | AnySchema:
        if isinstance(type, TypeAliasType):
            type = type.__value__

        if not isinstance(type, Type) and type in self.generic_mapping:
            type = self.generic_mapping[type]

        for pred, hook in self.build_rules:
            if pred(type):
                return hook(type, is_response)

        if has(type) or is_dataclass(type) or issubclass(type, Struct):
            # components are build elsewhere, here we just reference the component
            name = self._name_for(type, is_response)
            if name not in self._components:
                self.make_component(type, name, is_response=is_response)
            return Reference(f"#/components/schemas/{name}")

        raise TypeError(f"type of {type} is not supported yet")

    def make_component(self, t: type, name, is_response=False):
        self._components[name] = self.build_component(t, is_response=is_response)

    def build_component(self, type: Any, is_response=False) -> Schema:
        properties = {}
        if is_generic(type):
            self.generic_mapping.update(self._make_generic_mapping(type))
        required = []
        example = {}

        if isinstance(type, (StructType, DataclassType)):
            fields = type.fields
        elif issubclass(type, Struct):
            fields: tuple[Field] = type_info(type).fields  # ty: ignore[missing-attribute]
        else:
            f = at_fields if has(type) else dt_fields
            fields = f(type)

        for a in fields:
            if a.type is None:
                continue

            a_type = a.type
            if not isinstance(a_type, Type) and a_type in self.generic_mapping:
                a_type = self.generic_mapping[a_type]

            schema = self.get_schema_for_type(a_type, is_response=is_response)
            properties[a.name] = schema
            if (
                a.default is NOTHING
                or isinstance(a.default, _MISSING_TYPE)
                or a.default is NODEFAULT
            ):
                required.append(a.name)

            if not isinstance(a, Field) and a.metadata:
                e = a.metadata.get("example")
                example[a.name] = e

        return Schema(
            type=Schema.Type.OBJECT,
            properties=properties,
            required=required,
            example=example,
        )

    def build_security_component(self, type) -> SecurityScheme:
        if isinstance(type, ApiKey):
            return ApiKeySecurityScheme(in_=type.kind, description=type.description)
        if isinstance(type, Http):
            return HttpSecurityScheme(
                scheme=type.scheme, bearerFormat=type.bearer_format
            )
        if isinstance(type, OpenId):
            return OpenIdSecurityScheme(openIdConnectUrl=type.connect_url)
        if isinstance(type, OAuth2):
            flows = {
                k: OAuth2SecuritySchemeFlows(
                    scopes=f.scopes,
                    authorizationUrl=f.authorization_url,
                    tokenUrl=f.token_url,
                    refreshUrl=f.refresh_url,
                )
                for k, f in type.flows.items()
            }
            return OAuth2SecurityScheme(flows=flows, description=type.description)
        raise TypeError(f"type of {type} is not supported")

    def default_build_rules(self) -> list[tuple[Predicate, BuildHook]]:
        """Set up the default build rules."""
        rules = super().default_build_rules() + [
            (lambda t: is_tuple(t) or is_sequence(t), self._handle_array),
            (is_mapping, self._handle_mapping),
            (is_literal, self._handle_literal),
            (is_union_type, self._handle_union),
            (is_file, self._handle_file),
        ]

        if has_msgspec:
            rules = [
                (
                    lambda t: MSGSPEC_PRIMITIVES_TO_OPENAPI.__contains__(type(t)),
                    lambda t, _: MSGSPEC_PRIMITIVES_TO_OPENAPI[type(t)](),
                ),
                (lambda t: type(t) is DictType, self._handle_msgspec_dict),
                (lambda t: type(t) is LiteralType, self._handle_msgspec_literal),
                (lambda t: type(t) is UnionType, self._handle_msgspec_union),
                (
                    lambda t: type(t) in (DataclassType, StructType),
                    self._handle_msgspec_refrence,
                ),
                (
                    lambda t: type(t) in (ListType, TupleType, VarTupleType),
                    self._handle_msgspec_array,
                ),
            ] + rules
        return rules

    def _handle_array(self, t, _) -> ArraySchema:
        args = get_args(t)
        arg = args[0] if args else None
        if is_tuple(arg):
            inner = get_args(arg)
            if len(inner) > 1 and inner[1] is not ...:
                raise TypeError("tuples need to be homogeneous")
            return ArraySchema(self._handle_array(arg, _))

        if is_sequence(arg):
            return ArraySchema(self._handle_array(arg, _))
        inner = self.get_schema_for_type(arg) if arg else Schema()
        return ArraySchema(inner)

    def _handle_file(self, t, is_response) -> Schema:
        if is_annotated(t):
            format = get_args(t)[1]  # Annotated[UploadedFile, "uri"]
        else:
            format = "binary" if not is_response else "uri"
            self._has_file = True

        return Schema(Schema.Type.STRING, format=format)

    def _handle_union(self, type, _) -> OneOfSchema:
        refs: list[Reference | AnySchema] = []
        for arg in type.__args__:
            refs.append(self.get_schema_for_type(arg))
        return OneOfSchema(refs)

    def _handle_mapping(self, type, _):
        # Dicts also get created inline.
        args = get_args(type)

        key_type, value_type = args if len(args) == 2 else (Any, Any)
        # OpenAPI doesn't support anything else.
        if key_type not in (Any, str):
            raise TypeError(f"Can't handle {type}")

        value_schema = self.get_schema_for_type(value_type)
        return Schema(Schema.Type.OBJECT, additionalProperties=value_schema)

    def _handle_literal(self, type, _):
        ty = get_args(type)
        if sch := PYTHON_PRIMITIVES_TO_OPENAPI.get(ty, False):
            schema = sch()
            schema.enum = list(type.__args__)
            return schema
        else:
            return Schema(Schema.Type.STRING, enum=list(type.__args__))

    def _make_generic_mapping(self, type: type[Any]) -> dict:
        """A mapping of TypeVars to their actual bound types."""
        res = {}

        for arg, param in zip(
            type.__args__, type.__origin__.__parameters__, strict=True
        ):
            res[param] = arg

        return res

    def _name_for(self, type: Any, is_response=False) -> str:
        if (type, is_response) not in self.names:
            name = (
                type.__name__ if not is_generic(type) else self._make_generic_name(type)
            )
            counter = 2
            while name in self.names.values():
                name = f"{type.__name__}{counter}"
                counter += 1
            self.names[(type, is_response)] = name
        return self.names[(type, is_response)]

    def _make_generic_name(self, type: type[Any]) -> str:
        """Used for generic attrs classes (Generic[int] instead of just Generic)."""
        return type.__name__ + "[" + ", ".join(t.__name__ for t in type.__args__) + "]"

    def _handle_msgspec_dict(self, type, _) -> Schema:
        k = type.key_type
        if not isinstance(k, (AnyType, StrType)):
            raise TypeError(
                f"dictionary needs to have a key of type str or Any, used {k}"
            )
        v = self.get_schema_for_type(type.value_type, _)
        return Schema(Schema.Type.OBJECT, additionalProperties=v)

    def _handle_msgspec_array(self, type, _) -> ArraySchema:
        if isinstance(type, (ListType, VarTupleType)):
            t = type.item_type
        if isinstance(type, TupleType):
            if len(type.item_types) > 1:
                raise TypeError("tuples need to be homogeneous")
            t = type.item_types[0]
        return ArraySchema(self.get_schema_for_type(t, _))

    def _handle_msgspec_union(self, type, _) -> OneOfSchema:
        refs = []
        for t in type.types:
            refs.append(self.get_schema_for_type(t, _))
        return OneOfSchema(refs)

    def _handle_msgspec_literal(self, t, _) -> Schema:
        literals = t.values
        if sch := PYTHON_PRIMITIVES_TO_OPENAPI.get(type(literals[0]), False):
            schema = sch()
            schema.enum = list(literals)
            return schema
        return Schema(Schema.Type.STRING, enum=list(literals))

    def _handle_msgspec_refrence(self, t, _) -> Reference:
        name = self._name_for(t.cls, _)
        if name not in self._components:
            self.make_component(t, name, is_response=_)
        return Reference(f"#/components/schemas/{name}")
