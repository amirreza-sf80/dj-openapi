from cattrs import override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from cattrs.preconf.json import make_converter

from dj_openapi.data import (
    AnySchema,
    ApiKeySecurityScheme,
    ArraySchema,
    HttpSecurityScheme,
    OneOfSchema,
    OpenIdSecurityScheme,
    Operation,
    Parameter,
    Reference,
    Schema,
)

converter = make_converter(omit_if_default=True)


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
    Parameter, make_dict_structure_fn(Parameter, converter, kind=override(rename="in"))
)
converter.register_structure_hook(
    Reference, make_dict_structure_fn(Reference, converter, ref=override(rename="$ref"))
)
converter.register_structure_hook(
    Operation,
    make_dict_structure_fn(
        Operation, converter, request_body=override(rename="requestBody")
    ),
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
        bearer_format=override(rename="bearerFormat"),
        type=override(omit_if_default=False),
    ),
)
converter.register_unstructure_hook(
    OpenIdSecurityScheme,
    make_dict_unstructure_fn(
        OpenIdSecurityScheme,
        converter,
        open_id_connect_url=override(rename="openIdConnectUrl"),
        type=override(omit_if_default=False),
    ),
)

converter.register_unstructure_hook(
    Operation,
    make_dict_unstructure_fn(
        Operation, converter, request_body=override(rename="requestBody")
    ),
)
converter.register_unstructure_hook(
    Reference,
    make_dict_unstructure_fn(Reference, converter, ref=override(rename="$ref")),
)
converter.register_unstructure_hook(
    Parameter,
    make_dict_unstructure_fn(
        Parameter, converter, _cattrs_omit_if_default=True, kind=override(rename="in")
    ),
)
converter.register_unstructure_hook(
    ArraySchema,
    make_dict_unstructure_fn(
        ArraySchema, converter, type=override(omit_if_default=False)
    ),
)
