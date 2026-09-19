from collections.abc import Sequence
from functools import wraps
from typing import Any

from dj_openapi.typing import (
    DECORATOR_FIELDS,
    FORM_BODY,
    QUERY_STRING,
    REQUEST_BODY,
    RESPONSE_BODY,
)

from .data import METHOD, DecoratorFields, Metadata


def open_api(api: dict[METHOD, dict[DECORATOR_FIELDS, Any] | DecoratorFields]):
    def decor(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        if not hasattr(func, "metadata"):
            func.metadata = []

        for method, data in api.items():
            if isinstance(data, dict):
                metadata = Metadata(
                    method=method,
                    qs=data.get("qs", None),
                    request=data.get("request_body", None),
                    response=data.get("response", None),
                    form=data.get("form_body", None),
                    tags=data.get("tags", ()),
                )
            else:
                metadata = Metadata(
                    method=method,
                    qs=data.qs,
                    request=data.request_body,
                    response=data.response,
                    form=data.form_body,
                    tags=data.tags,
                )
            func.metadata.append(metadata)
            func.api = True
        return wraps(func)(inner)

    return decor


def get(
    qs: QUERY_STRING = None,
    response: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api({"get": DecoratorFields(qs=qs, response=response, tags=tags)})


def post(
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response: RESPONSE_BODY = None,
    form_body: FORM_BODY = None,
    tags: Sequence[str] = (),
):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "post": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response=response,
                form_body=form_body,
                tags=tags,
            )
        }
    )


def put(
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "put": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response=response,
                tags=tags,
            )
        }
    )


def patch(
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "patch": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response=response,
                tags=tags,
            )
        }
    )


def delete(
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "delete": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response=response,
                tags=tags,
            )
        }
    )


def query(
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "query": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response=response,
                tags=tags,
            )
        }
    )


def head(tags: Sequence[str] = ()):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "head": DecoratorFields(
                qs=None, request_body=None, response=None, form_body=None, tags=tags
            )
        }
    )


def options(tags: Sequence[str] = ()):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "options": DecoratorFields(
                qs=None, request_body=None, response=None, form_body=None, tags=tags
            )
        }
    )


def trace(tags: Sequence[str] = ()):
    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "trace": DecoratorFields(
                qs=None, request_body=None, response=None, form_body=None, tags=tags
            )
        }
    )
