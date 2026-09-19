from django.http import HttpResponse

from dj_openapi import get, head, options, post, trace

from .data import Person, Workplace


@get(qs={"something": str}, tags=("things",))
def my_view(request):
    return HttpResponse()


@get(qs={"something": str}, tags=("things",), response={200: Person})
def person_view(request):
    return HttpResponse()


@trace()
@options()
@head()
@post(
    qs={"something": str},
    tags=("things", "others"),
    request_body=Person,
    response={200: [str, int]},
)
def person_post_view(request):
    return HttpResponse()


@get(response={200: Workplace, 404: str}, tags=("places",))
def workplace_view(request):
    return HttpResponse()
