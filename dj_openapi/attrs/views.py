from django.http import HttpResponse

from dj_openapi.discover import make_openapi_spec
from dj_openapi.settings import JSON_DUMP_PATH, YAML_DUMP_PATH

from .structure import json_serializer as openapi_converter


def serve_openapi(request):
    if JSON_DUMP_PATH.exists():
        with open(JSON_DUMP_PATH, "r") as f:
            return HttpResponse(f.read(), status=200, content_type="application/json")
    if YAML_DUMP_PATH.exists():
        with open(YAML_DUMP_PATH, "r") as f:
            return HttpResponse(f.read(), status=200, content_type="application/yaml")

    openapi = make_openapi_spec()

    un = openapi_converter.unstructure(openapi)  # ty: ignore[unresolved-attribute]
    payload = openapi_converter.dumps(un)  # ty: ignore[unresolved-attribute]
    return HttpResponse(payload, status=200, content_type="application/json")
