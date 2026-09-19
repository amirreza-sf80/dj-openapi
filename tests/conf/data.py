from datetime import date
from decimal import Decimal
from typing import Any, Literal

from attrs import define
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
    name: CharField
    address: CharField
    is_active: BooleanField
    income: DecimalField
    employe_cound: IntegerField
    creation_date: DateField
    opening_time: TimeField
    start_holidy: DateTimeField
