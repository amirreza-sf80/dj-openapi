from django.http import HttpResponse
from django_cattrs_fields.converters.msgspec import serializer

from dj_openapi.discover import make_openapi_spec

from .structure import converter as openapi_converter


def serve_openapi(request):
    openapi = make_openapi_spec()

    payload = serializer.dumps(openapi_converter.unstructure(openapi))
    return HttpResponse(payload, status=200, content_type="application/json")
