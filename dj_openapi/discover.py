from collections.abc import Callable, Iterable
from functools import lru_cache
from importlib import import_module
from re import compile, sub

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.urls.resolvers import RoutePattern
from django.utils.module_loading import import_string

from dj_openapi.data import API, Info, OpenAPI
from dj_openapi.typing import DISCOVERER, PATTERNS, SchemaProtocol


def discoverer(patterns: PATTERNS, prefix="", exclude=None) -> list[API]:
    api_patterns: list[API] = list()

    def _inner(patterns: Iterable[URLPattern | URLResolver], prefix):
        for i in patterns:
            if isinstance(i.pattern, RoutePattern):
                _route = i.pattern._route
            else:
                _route = i.pattern._regex

            if isinstance(i, URLPattern):
                view = i.callback
                api = getattr(view, "api", False)
                if not api:
                    continue
                name = i.name
                if exclude and name in exclude:
                    continue
                url = f"{prefix}{_route}"
                metadata = view.metadata  # ty: ignore[unresolved-attribute]
                api_patterns.append(API(view=view, url=url, name=name, metadata=metadata))
            else:
                _inner(i.url_patterns, _route)  # ty: ignore[invalid-argument-type]

    _inner(patterns, prefix)
    return api_patterns


_angle_path_with_conv_pattern = compile(r"<([a-zA-Z_]+:[a-zA-Z_]+)>")
_angle_path_pattern = compile(r"<([a-zA-Z_]+)>")


def strip_path_param_prefix(path: str) -> str:
    return sub(
        _angle_path_with_conv_pattern, lambda m: f"{{{m.group(1).split(':')[1]}}}", path
    )


def parse_angle_path_params(path_str: str) -> list[str]:
    return [p.split(":")[0] for p in _angle_path_pattern.findall(path_str)]


def parse_path_parameters(path):
    clean = strip_path_param_prefix(path)
    return parse_angle_path_params(clean)


def default_summary_transformer(handler: Callable, name: str) -> str:
    return name.replace("_", " ").title()


def default_description_transformer(handler: Callable, name: str) -> str | None:
    """Use the handler docstring, if present."""
    return getattr(handler, "__doc__", None)


OPENAPI_TITLE = getattr(settings, "DJANGO_OPENAPI_TITLE", "OpenAPI")
OPENAPI_VERSION = getattr(settings, "DJANGO_OPENAPI_VERSION", "1.0")
OPENAPI_PREFIX = getattr(settings, "DJANGO_OPENAPI_PREFIX", "")
OPENAPI_EXCLUDE = getattr(settings, "DJANGO_OPENAPI_EXCLUDE", None)
OPENAPI_SCHEMA_HANDLER = getattr(
    settings, "DJANGO_OPENAPI_SCHEMA_HANDLER", ""
)  # TODO: provide a default
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


@lru_cache
def make_openapi_spec(
    title: str = OPENAPI_TITLE,
    version: str = OPENAPI_VERSION,
    exclude: set[str] | None = OPENAPI_EXCLUDE,
    prefix: str = OPENAPI_PREFIX,
    patterns: Iterable[URLPattern | URLResolver] | None = None,
) -> OpenAPI:
    if not patterns:
        url_conf = import_module(settings.ROOT_URLCONF)
        patterns: Iterable[URLPattern | URLResolver] = url_conf.urlpatterns

    _discoverer: DISCOVERER = import_string(OPENAPI_DISCOVERER) if OPENAPI_DISCOVERER else discoverer  # fmt: skip
    api_patterns = _discoverer(patterns, prefix, exclude)

    SchemaHandler: type[SchemaProtocol] = import_string(OPENAPI_SCHEMA_HANDLER)
    # fmt: off
    schema_handler = SchemaHandler(
        api_patterns,
        import_string(OPENAPI_PATH_PARSER) if OPENAPI_PATH_PARSER else parse_path_parameters,
        import_string(OPENAPI_SUMMARY_TRANSFORMER) if OPENAPI_SUMMARY_TRANSFORMER else default_summary_transformer,
        import_string(OPENAPI_DESCRIPTION_TRANSFORMER) if OPENAPI_DESCRIPTION_TRANSFORMER else default_description_transformer,
    )
    # fmt: on
    schema_handler.build()

    open_api = OpenAPI(
        openapi="3.2.0",
        info=Info(title, version),
        paths=schema_handler.path_items,
        components=schema_handler.components,
    )
    return open_api
