from django.urls import path

from dj_openapi.attrs.views import (
    serve_openapi,
)
from dj_openapi.views import serve_elements, serve_redoc, serve_swaggerui

from .views import (
    my_view,
    person_post_view,
    person_view,
    person_view_content,
    workplace_needs_qs_view,
    workplace_no_need_qs_view,
    workplace_options_view,
    workplace_view,
    workplace_weird_view,
)

urlpatterns = [
    path("", my_view, name="my-view"),
    path("person/", person_view, name="person-view"),
    path("person/post/", person_post_view, name="person-post-view"),
    path("person/content/", person_view_content, name="person-view-content"),
    path("workplace/", workplace_view, name="workplace-view"),
    path("workplace/options/", workplace_options_view, name="workplace-options-view"),
    path("workplace/weird/", workplace_weird_view, name="workplace-weird-view"),
    path("workplace/qs/need/", workplace_needs_qs_view, name="workplace-qs-view"),
    path("workplace/qs/noneed/", workplace_no_need_qs_view, name="workplace-qs-view"),
    path("openapi.json", serve_openapi),
    path("swagger/", serve_swaggerui),
    path("redoc/", serve_redoc),
    path("elements/", serve_elements),
]
