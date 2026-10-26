from decimal import Decimal
from typing import Literal

from django.http import HttpResponse

from dj_openapi import get, head, open_api, options, post, trace
from dj_openapi.data import ApiKey, Http, OAuth2, OAuth2Flows, OpenId, QueryParam

from .data import Person, Workplace


@get(qs={"something": str}, tags=("things",), security=ApiKey(name="whee"))
def my_view(request):
    return HttpResponse()


@get(
    qs={"something": str},
    tags=("things",),
    response_body={200: Person},
    content_type=["application/json", "text/plain"],
    security=Http(name="whooo", scheme="basic"),
)
def person_view_content(request):
    return HttpResponse()


@get(
    qs={"something": Literal["sooo", "beee"]},
    tags=("things",),
    response_body={200: Person},
    security=OpenId(
        name="whaaa",
        connect_url="https://example.com/.well-known/openid-configuration",
        scopes=["write"],
    ),
)
def person_view(request):
    return HttpResponse()


@trace
@options
@head
@post(
    qs={"something": str},
    tags=("things", "others"),
    request_body=Person,
    response_body={200: [str, int]},
    content_type=["application/json", "text/plain"],
    security=Http(name="doo", scheme="bearer", bearer_format="jwt"),
)
def person_post_view(request):
    return HttpResponse()


@get(
    response_body={200: Workplace, 404: str},
    tags=("places",),
    security=OAuth2(
        "dee",
        scopes=["write", "read"],
        description="deeeee",
        flows={
            "implicit": OAuth2Flows(
                authorization_url="https://api.example.com/oauth2/authorize",
                scopes={
                    "read": "reads stuff",
                    "write": "write stuff",
                    "readwrite": "read and write",
                },
            )
        },
    ),
)
def workplace_view(request):
    return HttpResponse()


@options
def workplace_options_view(request):
    return HttpResponse()


@open_api(
    {
        "get": {
            "qs": {"weird": Decimal},
            "response_body": {404: str},
            "tags": ["wheee"],
        },
        "post": {
            "qs": {"weird": Decimal},
            "request_body": str,
            "response_body": {404: str},
            "tags": ["wheee"],
        },
        "head": {},
        "options": {},
    }
)
def workplace_weird_view(request):
    return HttpResponse()


@get(
    qs={
        "whee": QueryParam(
            required=True, description="whee qs", type=Literal["wh", "th"]
        )
    }
)
def workplace_needs_qs_view(request):
    return HttpResponse()


@get(qs={"whoo": QueryParam(required=False, description="no whoo qs", type=Decimal)})
def workplace_no_need_qs_view(request):
    return HttpResponse()
