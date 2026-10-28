from django.http import HttpResponse

from dj_openapi.discover import make_openapi_spec
from dj_openapi.exceptions import SerializerNotConfigured
from dj_openapi.settings import JSON_DUMP_PATH, YAML_DUMP_PATH

from .structure import json_serializer, yaml_serializer


def serve_openapi(request):
    if JSON_DUMP_PATH.exists():
        with open(JSON_DUMP_PATH) as f:
            return HttpResponse(f.read(), status=200, content_type="application/json")
    if YAML_DUMP_PATH.exists():
        with open(YAML_DUMP_PATH) as f:
            return HttpResponse(f.read(), status=200, content_type="application/yaml")

    openapi = make_openapi_spec()

    if json_serializer:
        un = json_serializer.unstructure(openapi)
        payload = json_serializer.dumps(un)
        return HttpResponse(payload, status=200, content_type="application/json")
    elif yaml_serializer:
        un = yaml_serializer.unstructure(openapi)
        payload = yaml_serializer.dumps(un)
        return HttpResponse(payload, status=200, content_type="application/yaml")
    else:
        raise SerializerNotConfigured()
