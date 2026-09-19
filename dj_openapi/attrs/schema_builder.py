from collections.abc import Callable, Iterable
from inspect import signature
from typing import Any, TypeAliasType

from attrs import NOTHING, fields, has
from cattrs._compat import get_args, is_generic, is_literal, is_tuple, is_union_type
from cattrs.cols import is_mapping, is_sequence

from dj_openapi.base_schema_builder import (
    PYTHON_PRIMITIVES_TO_OPENAPI,
    BaseSchemaBuilder,
)
from dj_openapi.data import (
    API,
    METHOD,
    URL,
    AnySchema,
    ArraySchema,
    Components,
    MediaType,
    Metadata,
    OneOfSchema,
    Operation,
    Parameter,
    PathItem,
    Reference,
    RequestBody,
    Response,
    Schema,
    StatusCodeType,
    get_http_response_description,
)
from dj_openapi.typing import (
    DESCRIPTION_TRANSFORMER,
    PATH_PARAM_PARSER,
    SUMMARY_TRANSFORMER,
)

type Predicate = Callable[[Any], bool]
type BuildHook = Callable[[Any], Schema]


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
        self.names: dict[type, str] = {}
        self._components: dict[str, AnySchema | Reference] = {}
        self.path_items: dict[URL, PathItem] = {}
        self.generic_mapping = {}

    @property
    def components(self) -> Components:
        return Components(self._components)

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
            self.path_items[api.url] = PathItem(**item)

    def build_operation(
        self,
        api: API,
        metadata: Metadata,
        path_param_parser,
        summary_reader,
        description_reader,
    ) -> Operation:
        request_bodies = {}
        resps: dict[StatusCodeType, Response] = {"200": Response(description="OK")}
        params: list[Parameter] = []
        sig = signature(api.view, eval_str=True)
        path_params = path_param_parser(api.url)
        if path_params:
            path_params = path_params[1]

        # path parameters
        for path_param in path_params:
            if path_param not in sig.parameters:
                raise ValueError(f"Path parameter {path_param} not found")
            t = sig.parameters[path_param].annotation
            params.append(
                Parameter(
                    path_param,
                    Parameter.Kind.PATH,
                    True,
                    PYTHON_PRIMITIVES_TO_OPENAPI.get(t),
                )
            )

        # request bodies
        if metadata.request:
            if not isinstance(metadata.request, Iterable):
                request_bodies["application/json"] = MediaType(
                    self.get_schema_for_type(metadata.request)
                )
            else:
                request_bodies["application/json"] = MediaType(
                    OneOfSchema([self.get_schema_for_type(r) for r in metadata.request])
                )

        # request forms
        if metadata.form:
            if not isinstance(metadata.form, Iterable):
                request_bodies["application/x-www-form-urlencoded"] = MediaType(
                    self.get_schema_for_type(metadata.form)
                )
            else:
                request_bodies["application/x-www-form-urlencoded"] = MediaType(
                    OneOfSchema([self.get_schema_for_type(r) for r in metadata.form])
                )

        req_body = None
        if request_bodies:
            req_body = RequestBody(request_bodies, required=True)

        # query strings
        if metadata.qs:
            for q, t in metadata.qs.items():
                ty = self.get_schema_for_type(t)
                params.append(Parameter(q, Parameter.Kind.QUERY, False, ty))

        # response
        if metadata.response:
            for stat, res in metadata.response.items():
                if not isinstance(res, Iterable):
                    r = MediaType(self.get_schema_for_type(res))
                elif res:
                    r = MediaType(
                        OneOfSchema([self.get_schema_for_type(r) for r in res])
                    )
                else:
                    r = None

                desc = get_http_response_description(stat)
                if isinstance(stat, int) and (stat < 200 or stat == 204 or stat == 304):
                    resp = Response(desc)
                else:
                    resp = Response(desc, content={"application/json": r} if r else {})

                resps[str(stat)] = resp

        return Operation(
            resps,
            params,
            request_body=req_body,
            summary=summary_reader(api.view, api.name),
            tags=metadata.tags,
            operationId=api.name,
            description=description_reader(api.view, api.name),
        )

    def get_schema_for_type(self, type: Any) -> Reference | AnySchema:
        if isinstance(type, TypeAliasType):
            type = type.__value__

        if type in self.generic_mapping:
            type = self.generic_mapping[type]

        # First check inline types.
        if type in PYTHON_PRIMITIVES_TO_OPENAPI:
            return PYTHON_PRIMITIVES_TO_OPENAPI[type]
        if type is Any:
            return Schema()
        if is_tuple(type) or is_sequence(type):
            # Arrays get created inline.
            return self._handle_array(type)

        if is_mapping(type):
            # Dicts also get created inline.
            args = get_args(type)

            key_type, value_type = args if len(args) == 2 else (Any, Any)
            # OpenAPI doesn't support anything else.
            if key_type not in (Any, str):
                raise TypeError(f"Can't handle {type}")

            value_schema = self.get_schema_for_type(value_type)
            return Schema(Schema.Type.OBJECT, additionalProperties=value_schema)

        if is_literal(type):
            ty = get_args(type)
            if ty in PYTHON_PRIMITIVES_TO_OPENAPI:
                schema = PYTHON_PRIMITIVES_TO_OPENAPI[ty]
                schema.enum = list(type.__args__)
                return schema
            else:
                return Schema(Schema.Type.STRING, enum=list(type.__args__))

        if is_union_type(type):
            return self._handle_union(type)

        if has(type):
            # components are build elsewhere, here we just reference the component
            name = self._name_for(type)
            if name not in self._components:
                self.make_component(type)
            return Reference(f"#/components/schemas/{name}")

        raise TypeError(f"type of {type} is not supported yet")

    def make_component(self, t: type):
        for pred, hook in self.build_rules:
            if pred(t):
                break
        else:
            raise TypeError(f"can't handle {t}")

        name = self._name_for(t)
        self._components[name] = hook(t)

    def build_attrs_component(self, type: Any) -> Schema:
        properties = {}
        if is_generic(type):
            self.generic_mapping.update(self._make_generic_mapping(type))
        required = []

        for a in fields(type):
            if a.type is None:
                continue

            a_type = a.type
            if a_type in self.generic_mapping:
                a_type = self.generic_mapping[a_type]

            schema = self.get_schema_for_type(a_type)
            properties[a.name] = schema
            if a.default is NOTHING:
                required.append(a.name)

        return Schema(type=Schema.Type.OBJECT, properties=properties, required=required)

    def default_build_rules(self) -> list[tuple[Predicate, BuildHook]]:
        """Set up the default build rules."""
        # For circular deps.
        return super().default_build_rules() + [
            (has, self.build_attrs_component),
        ]

    def _handle_array(self, t) -> ArraySchema:
        args = get_args(t)
        arg = args[0] if args else None
        if is_tuple(arg):
            inner = get_args(arg)
            if len(inner) > 1 and inner[1] is not ...:
                raise TypeError("tuples need to be homogenous")
            return ArraySchema(self._handle_array(arg))

        if is_sequence(arg):
            return ArraySchema(self._handle_array(arg))
        inner = self.get_schema_for_type(arg) if arg else Schema()
        return ArraySchema(inner)

    def _handle_union(self, type) -> OneOfSchema:
        refs: list[Reference | AnySchema] = []
        for arg in type.__args__:
            refs.append(self.get_schema_for_type(arg))
        return OneOfSchema(refs)

    def _make_generic_mapping(self, type: type[Any]) -> dict:
        """A mapping of TypeVars to their actual bound types."""
        res = {}

        for arg, param in zip(
            type.__args__, type.__origin__.__parameters__, strict=True
        ):
            res[param] = arg

        return res

    def _name_for(self, type: Any) -> str:
        if type not in self.names:
            name = (
                type.__name__ if not is_generic(type) else self._make_generic_name(type)
            )
            counter = 2
            while name in self.names.values():
                name = f"{type.__name__}{counter}"
                counter += 1
            self.names[type] = name
        return self.names[type]

    def _make_generic_name(self, type: type[Any]) -> str:
        """Used for generic attrs classes (Generic[int] instead of just Generic)."""
        return type.__name__ + "[" + ", ".join(t.__name__ for t in type.__args__) + "]"
