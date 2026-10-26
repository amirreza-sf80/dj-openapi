from datetime import date, datetime, time
from decimal import Decimal
from types import NoneType
from typing import Any

from dj_openapi.data import Schema
from dj_openapi.settings import USER_BUILD_RULES
from dj_openapi.typing import BuildHook, Predicate

PYTHON_PRIMITIVES_TO_OPENAPI: dict[type | None, Schema] = {
    str: Schema(Schema.Type.STRING),
    int: Schema(Schema.Type.INTEGER),
    bool: Schema(Schema.Type.BOOLEAN),
    float: Schema(Schema.Type.NUMBER, format="double"),
    Decimal: Schema(Schema.Type.NUMBER, format="double"),
    bytes: Schema(Schema.Type.STRING, format="binary"),
    date: Schema(Schema.Type.STRING, format="date"),
    datetime: Schema(Schema.Type.STRING, format="date-time"),
    time: Schema(Schema.Type.STRING, format="time"),
    NoneType: Schema(Schema.Type.NULL),
}


class BaseSchemaBuilder:
    def default_build_rules(self) -> list[tuple[Predicate, BuildHook]]:
        """Set up the default build rules."""
        # For circular deps.
        return USER_BUILD_RULES + [
            (
                PYTHON_PRIMITIVES_TO_OPENAPI.__contains__,
                lambda t, _: PYTHON_PRIMITIVES_TO_OPENAPI[t],
            ),
            (lambda t: t is Any, lambda _, __: Schema()),
        ]
