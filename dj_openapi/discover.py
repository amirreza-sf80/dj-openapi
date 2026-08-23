from collections.abc import Iterable
from functools import lru_cache
from importlib import import_module
from re import compile, sub

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.urls.resolvers import RoutePattern
from django.utils.module_loading import import_string

from dj_openapi.data import API, OpenAPI, Info


def discover(patterns: Iterable[URLPattern | URLResolver], prefix="", exclude=None) -> set[API]:
    api_patterns: set[API] = set()

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
                api_patterns.add(API(view=view, url=url, name=name, metadata=metadata))
            else:
                _inner(i.url_patterns, _route)  # ty: ignore[invalid-argument-type]

    _inner(patterns, prefix)
    return api_patterns


_angle_path_with_conv_pattern = compile(r"<([a-zA-Z_]+:[a-zA-Z_]+)>")
_angle_path_pattern = compile(r"<([a-zA-Z_]+)>")


def strip_path_param_prefix(path: str) -> str:
    return sub(_angle_path_with_conv_pattern, lambda m: f"{{{m.group(1).split(':')[1]}}}", path)


def parse_curly_path_params(path_str: str) -> list[str]:
    return [p.split(":")[0] for p in _angle_path_pattern.findall(path_str)]


OPENAPI_TITLE = getattr(settings, "DJANGO_OPENAPI_TITLE", "OpenAPI")
OPENAPI_VERSION = getattr(settings, "DJANGO_OPENAPI_VERSION", "1.0")
OPENAPI_EXCLUDE = getattr(settings, "DJANGO_OPENAPI_EXCLUDE", None)
OPENAPI_SCHEMA_HANDLER = getattr(
    settings, "DJANGO_OPENAPI_SCHEMA_HANDLER", ""
)  # TODO: provide a default


@lru_cache
def make_openapi_spec(
    title: str = OPENAPI_TITLE,
    version: str = OPENAPI_VERSION,
    exclude: set[str] | None = OPENAPI_EXCLUDE,
    prefix: str = "",
    patterns: Iterable[URLPattern | URLResolver] | None = None,
) -> OpenAPI:
    if not patterns:
        url_conf = import_module(settings.ROOT_URLCONF)
        patterns = url_conf.urlpatterns
    api_patterns = discover(patterns, prefix, exclude)

    schema_handler = import_string(OPENAPI_SCHEMA_HANDLER)(api_patterns)
    paths = schema_handler.get_paths()
    components = schema_handler.get_components()

    res = OpenAPI(
        openapi="3.2.0",
        info=Info(title, version),
        paths=paths,
        components=components,
    )
    return res
