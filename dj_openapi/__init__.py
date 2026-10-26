from collections.abc import Sequence
from functools import partial, wraps
from typing import Any

from dj_openapi.typing import (
    DECORATOR_FIELDS,
    FORM_BODY,
    QUERY_STRING,
    REQUEST_BODY,
    RESPONSE_BODY,
)

from .data import METHOD, DecoratorFields, Metadata, Security


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
                    response=data.get("response_body", None),
                    form=data.get("form_body", None),
                    tags=data.get("tags", ()),
                    content_type=data.get("content_type", "application/json"),
                    security=data.get("security", None),
                )
            else:
                metadata = Metadata(
                    method=method,
                    qs=data.qs,
                    request=data.request_body,
                    response=data.response_body,
                    form=data.form_body,
                    tags=data.tags,
                    content_type=data.content_type,
                    security=data.security,
                )
            func.metadata.append(metadata)
            func.api = True
        return wraps(func)(inner)

    return decor


def get(
    func=None,
    *,
    qs: QUERY_STRING = None,
    response_body: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(
            get,
            qs=qs,
            response_body=response_body,
            tags=tags,
            content_type=content_type,
            security=security,
        )

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "get": DecoratorFields(
                qs=qs,
                response_body=response_body,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def post(
    func=None,
    *,
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response_body: RESPONSE_BODY = None,
    form_body: FORM_BODY = None,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(
            post,
            qs=qs,
            request_body=request_body,
            response_body=response_body,
            form_body=form_body,
            tags=tags,
            content_type=content_type,
            security=security,
        )

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "post": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response_body=response_body,
                form_body=form_body,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def put(
    func=None,
    *,
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response_body: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(
            put,
            qs=qs,
            request_body=request_body,
            response_body=response_body,
            tags=tags,
            content_type=content_type,
            security=security,
        )

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "put": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response_body=response_body,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def patch(
    func=None,
    *,
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response_body: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(
            patch,
            qs=qs,
            request_body=request_body,
            response_body=response_body,
            tags=tags,
            content_type=content_type,
            security=security,
        )

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "patch": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response_body=response_body,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def delete(
    func=None,
    *,
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response_body: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(
            delete,
            qs=qs,
            request_body=request_body,
            response_body=response_body,
            tags=tags,
            content_type=content_type,
            security=security,
        )

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "delete": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response_body=response_body,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def query(
    func=None,
    *,
    qs: QUERY_STRING = None,
    request_body: REQUEST_BODY = None,
    response_body: RESPONSE_BODY = None,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(
            query,
            qs=qs,
            request_body=request_body,
            response_body=response_body,
            tags=tags,
            content_type=content_type,
            security=security,
        )

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "query": DecoratorFields(
                qs=qs,
                request_body=request_body,
                response_body=response_body,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def head(
    func=None,
    *,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(head, tags=tags, content_type=content_type, security=security)

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "head": DecoratorFields(
                qs=None,
                request_body=None,
                response_body=None,
                form_body=None,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def options(
    func=None,
    *,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(options, tags=tags, content_type=content_type, security=security)

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "options": DecoratorFields(
                qs=None,
                request_body=None,
                response_body=None,
                form_body=None,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)


def trace(
    func=None,
    *,
    tags: Sequence[str] = (),
    content_type: Sequence[str] | str = "application/json",
    security: Security | None = None,
):
    if not func:
        return partial(trace, tags=tags, content_type=content_type, security=security)

    if isinstance(tags, str):
        tags = (tags,)
    return open_api(
        {
            "trace": DecoratorFields(
                qs=None,
                request_body=None,
                response_body=None,
                form_body=None,
                tags=tags,
                content_type=content_type,
                security=security,
            )
        }
    )(func)
