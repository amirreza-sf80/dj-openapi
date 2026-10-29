from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Literal

from attrs import define, field
from django_cattrs_fields.fields import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    IntegerField,
    TimeField,
)


@define
class Car:
    type: str
    price: Decimal
    speed: int


@define
class Person:
    name: str
    age: int
    height: float | int
    birth: date
    info: dict[str, str]
    info2: dict[str, str | int]
    things: list[tuple[str]]
    other: tuple
    other2: tuple[str]
    other3: tuple[tuple[str]]
    other4: tuple[list[str]]
    other5: tuple[str | int]
    other6: tuple[list[str | int]]
    emplyment_type: Literal["worker", "manager"]
    whatever: Any
    car: Car
    salary: Decimal | None = None


@define
class Workplace:
    name: CharField = field(metadata={"example": "linux HQ."})
    address: CharField = field(metadata={"example": "linus' home"})
    is_active: BooleanField = field(metadata={"example": True})
    income: DecimalField = field(metadata={"example": 0.0})
    employe_count: IntegerField = field(metadata={"example": 1})
    creation_date: DateField = field(
        metadata={"example": date(year=1991, month=9, day=17)}
    )
    opening_time: TimeField = field(metadata={"example": time(hour=7, minute=0)})
    start_holidy: DateTimeField = field(
        metadata={"example": datetime(year=2060, month=12, day=29, hour=23, minute=59)}
    )
