from django.urls import path

from dj_openapi.attrs.views import (
    serve_openapi,
)
from dj_openapi.views import serve_elements, serve_redoc, serve_swaggerui

from .views import my_view, person_post_view, person_view, workplace_view

urlpatterns = [
    path("", my_view, name="my-view"),
    path("person/", person_view, name="person-view"),
    path("person/post", person_post_view, name="person-post-view"),
    path("workplace", workplace_view, name="workplace-view"),
    path("openapi.json", serve_openapi),
    path("swagger/", serve_swaggerui),
    path("redoc/", serve_redoc),
    path("elements/", serve_elements),
]
