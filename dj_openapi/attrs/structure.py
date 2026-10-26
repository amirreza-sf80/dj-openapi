from cattrs import override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from django.utils.module_loading import import_string

from dj_openapi.data import (
    AnySchema,
    ApiKeySecurityScheme,
    ArraySchema,
    Components,
    HttpSecurityScheme,
    OAuth2SecurityScheme,
    OneOfSchema,
    OpenIdSecurityScheme,
    Parameter,
    Reference,
    Schema,
)
from dj_openapi.settings import JSON_SERIALIZER, YAML_SERIALIZER

json_serializer = None
yaml_serializer = None

if JSON_SERIALIZER:
    maker = JSON_SERIALIZER.endswith("make_converter")
    j = import_string(JSON_SERIALIZER)
    json_serializer = j(omit_if_default=True) if maker else j


if YAML_SERIALIZER:
    maker = YAML_SERIALIZER.endswith("make_converter")
    y = import_string(YAML_SERIALIZER)
    yaml_serializer = y(omit_if_default=True) if maker else y


def register(converter):
    def _structure_schemas(val, _):
        if "$ref" in val:
            return converter.structure(val, Reference)
        if "oneOf" in val:
            return converter.structure(val, OneOfSchema)

        if "type" not in val:
            return Schema()
        type = Schema.Type(val["type"])
        if type is Schema.Type.ARRAY:
            return converter.structure(val, ArraySchema)
        return converter.structure(val, Schema)

    def _structure_schema_or_ref(val, _) -> Schema | Reference:
        if "$ref" in val:
            return converter.structure(val, Reference)
        if "type" not in val:
            return Schema()
        return converter.structure(val, Schema)

    converter.register_structure_hook(AnySchema | Reference, _structure_schemas)
    converter.register_structure_hook(Schema | Reference, _structure_schema_or_ref)
    converter.register_structure_hook(
        Schema | ArraySchema | Reference,
        lambda v, _: (
            converter.structure(v, Reference)
            if "$ref" in v
            else (
                converter.structure(v, ArraySchema)
                if "items" in v
                else converter.structure(v, Schema)
            )
        ),
    )
    converter.register_structure_hook(
        bool | Schema | Reference,
        lambda v, _: (
            v
            if isinstance(v, bool)
            else (
                converter.structure(v, Reference)
                if "$ref" in v
                else converter.structure(v, Schema)
            )
        ),
    )

    converter.register_structure_hook(
        Reference,
        make_dict_structure_fn(Reference, converter, ref=override(rename="$ref")),
    )

    converter.register_unstructure_hook(
        ApiKeySecurityScheme,
        make_dict_unstructure_fn(
            ApiKeySecurityScheme,
            converter,
            in_=override(rename="in"),
            type=override(omit_if_default=False),
        ),
    )
    converter.register_unstructure_hook(
        HttpSecurityScheme,
        make_dict_unstructure_fn(
            HttpSecurityScheme,
            converter,
            type=override(omit_if_default=False),
        ),
    )
    converter.register_unstructure_hook(
        OAuth2SecurityScheme,
        make_dict_unstructure_fn(
            OAuth2SecurityScheme,
            converter,
            type=override(omit_if_default=False),
        ),
    )
    converter.register_unstructure_hook(
        OpenIdSecurityScheme,
        make_dict_unstructure_fn(
            OpenIdSecurityScheme,
            converter,
            type=override(omit_if_default=False),
        ),
    )

    converter.register_unstructure_hook(
        Components,
        make_dict_unstructure_fn(
            Components, converter, security_schemes=override(rename="securitySchemes")
        ),
    )
    converter.register_unstructure_hook(
        Reference,
        make_dict_unstructure_fn(Reference, converter, ref=override(rename="$ref")),
    )
    converter.register_unstructure_hook(
        Parameter,
        make_dict_unstructure_fn(
            Parameter,
            converter,
            _cattrs_omit_if_default=True,
            kind=override(rename="in"),
        ),
    )
    converter.register_unstructure_hook(
        ArraySchema,
        make_dict_unstructure_fn(
            ArraySchema, converter, type=override(omit_if_default=False)
        ),
    )


if json_serializer:
    register(json_serializer)
if yaml_serializer:
    register(yaml_serializer)
