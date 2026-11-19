from datetime import date, datetime, time
from decimal import Decimal
from types import NoneType
from typing import Any

from dj_openapi.data import (
    BoolSchema,
    BytesSchema,
    DateSchema,
    DateTimeSchema,
    DoubleSchema,
    IntSchema,
    NullSchema,
    Schema,
    StrSchema,
    TimeSchema,
)
from dj_openapi.settings import OPENAPI_PATH_TYPES, USER_BUILD_RULES
from dj_openapi.typing import BuildHook, Predicate

STR_TO_PYTHON = {
    "str": str,
    "int": int,
    "slug": str,
    "uuid": str,
    "path": str,
}
STR_TO_PYTHON.update(OPENAPI_PATH_TYPES)

PYTHON_PRIMITIVES_TO_OPENAPI: dict[type, type[Schema]] = {
    str: StrSchema,
    int: IntSchema,
    bool: BoolSchema,
    float: DoubleSchema,
    Decimal: DoubleSchema,
    bytes: BytesSchema,
    date: DateSchema,
    datetime: DateTimeSchema,
    time: TimeSchema,
    NoneType: NullSchema,
}


class BaseSchemaBuilder:
    def default_build_rules(self) -> list[tuple[Predicate, BuildHook]]:
        """Set up the default build rules."""
        # For circular deps.
        return USER_BUILD_RULES + [
            (
                PYTHON_PRIMITIVES_TO_OPENAPI.__contains__,
                lambda t, _: PYTHON_PRIMITIVES_TO_OPENAPI[t](),
            ),
            (lambda t: t is Any, lambda _, __: Schema()),
        ]
