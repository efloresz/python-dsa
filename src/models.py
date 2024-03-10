"""ORM (object-relational mapping) provides data structures for the application."""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import Literal

ClinicId = str
CatId = str
PersonId = str
VeterinarianId = str

id_field = field(default_factory=lambda: uuid.uuid4().hex)

now = dt.datetime.now


def round(datetime: dt.datetime) -> dt.datetime:
    """Floor the given datetime to"""
    return datetime.replace(minute=0, second=0, microsecond=0)


@dataclass
class Person:
    """A human who might or might not own a cat."""

    given_name: str
    surname: str

    id: PersonId = id_field


@dataclass
class Cat:
    """Store data about a cat."""

    name: str
    owner_id: PersonId

    age: int = 0  # years
    color: Literal['black', 'gray', 'orange', 'other'] = 'other'
    id: CatId = id_field
    lives: int = 9


@dataclass
class Clinic:
    """A clinic where veterinarians work to care for cats and owners."""

    name: str
    id: ClinicId = id_field


@dataclass
class Veterinarian:
    """A person who can treat cats."""

    clinic_id: ClinicId
    given_name: str
    license_number: str
    surname: str

    id: VeterinarianId = id_field


@dataclass
class Appointment:
    """A pet owner's appoint to see their vet at the clinic."""

    cat_id: CatId
    clinic_id: ClinicId
    owner_id: PersonId
    veterinarian_id: VeterinarianId

    start: dt.datetime = field(default_factory=lambda: round(now() + dt.timedelta(days=1)))
    duration: dt.timedelta = field(default_factory=lambda: dt.timedelta(minutes=30))
