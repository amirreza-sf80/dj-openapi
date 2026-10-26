from pathlib import Path

from django.conf import settings
from django.utils.module_loading import import_string

from dj_openapi.typing import BuildHook, Predicate

BASE_DIR = settings.BASE_DIR

_JSON_SERIALIZER = getattr(settings, "DJANGO_OPENAPI_JSON_SERIALIZER", "json")
_YAML_SERIALIZER = getattr(settings, "DJANGO_OPENAPI_YAML_SERIALIZER", None)
serializers = {
    "json": "cattrs.preconf.json.make_converter",
    "pyyaml": "cattrs.preconf.pyyaml.make_converter",
}
serializer_shortcuts = getattr(settings, "DJANGO_OPENAPI_SERIALIZER_SHORTCUTS", {})
serializers.update(serializer_shortcuts)
JSON_SERIALIZER = serializers.get(_JSON_SERIALIZER, _JSON_SERIALIZER)
YAML_SERIALIZER = serializers.get(_YAML_SERIALIZER, _YAML_SERIALIZER)


JSON_DUMP_NAME = getattr(settings, "DJANGO_OPENAPI_JSON_DUMP_NAME", "openapi.json")
JSON_DUMP_PATH = getattr(
    settings, "DJANGO_OPENAPI_DUMP_PATH", BASE_DIR / JSON_DUMP_NAME
)
YAML_DUMP_NAME = getattr(settings, "DJANGO_OPENAPI_YAML_DUMP_NAME", "openapi.yaml")
YAML_DUMP_PATH = getattr(
    settings, "DJANGO_OPENAPI_YAML_DUMP_PATH", BASE_DIR / YAML_DUMP_NAME
)
if not isinstance(JSON_DUMP_PATH, Path):
    JSON_DUMP_PATH = Path(JSON_DUMP_PATH)
if not isinstance(YAML_DUMP_PATH, Path):
    YAML_DUMP_PATH = Path(YAML_DUMP_PATH)

OPENAPI_TITLE = getattr(settings, "DJANGO_OPENAPI_TITLE", "OpenAPI")
OPENAPI_VERSION = getattr(settings, "DJANGO_OPENAPI_VERSION", "1.0")
OPENAPI_PREFIX = getattr(settings, "DJANGO_OPENAPI_PREFIX", "")
OPENAPI_EXCLUDE = getattr(settings, "DJANGO_OPENAPI_EXCLUDE", None)
OPENAPI_DISCOVERER = getattr(settings, "DJANGO_OPENAPI_DISCOVERER", "")
OPENAPI_PATH_PARSER = getattr(settings, "DJANGO_OPENAPI_PATH_PARSER", "")
OPENAPI_DESCRIPTION_TRANSFORMER = getattr(
    settings,
    "DJANGO_OPENAPI_DESCRIPTION_TRANSFORMER",
    "",
)
OPENAPI_SUMMARY_TRANSFORMER = getattr(
    settings,
    "DJANGO_OPENAPI_SUMMARY_TRANSFORMER",
    "",
)

_USER_BUILD_RULES: list[tuple[str | Predicate, str | BuildHook]] = getattr(
    settings, "CUSTOM_BUILD_RULES", []
)
USER_BUILD_RULES = []
for r in _USER_BUILD_RULES:
    USER_BUILD_RULES.append(
        (
            import_string(r[0]) if isinstance(r[0], str) else r[0],
            import_string(r[1]) if isinstance(r[1], str) else r[1],
        )
    )


# NOTE: remember to update this
schema_handlers = {"attrs": "dj_openapi.attrs.schema_builder.SchemaBuilder"}
schema_handler_shortcuts = getattr(
    settings, "DJANGO_OPENAPI_SCHEMA_HANDLER_SHORTCUTS", {}
)

schema_handlers.update(schema_handler_shortcuts)

_OPENAPI_SCHEMA_HANDLER = getattr(
    settings, "DJANGO_OPENAPI_SCHEMA_HANDLER", ""
)  # TODO: provide a default
OPENAPI_SCHEMA_HANDLER = schema_handlers.get(
    _OPENAPI_SCHEMA_HANDLER, _OPENAPI_SCHEMA_HANDLER
)
