"""Use `factory-boy` to define classes for generating data.

To learn more about `factory-boy`, see https://factoryboy.readthedocs.io/en/stable/introduction.html
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, TypeVar

import factory as fact
import petname
from factory import fuzzy

import models

T = TypeVar('T')


def flatten(list_of_lists: Iterable[list[T]]) -> list[T]:
    # ref: https://realpython.com/python-flatten-list/#how-to-flatten-a-list-of-lists-with-a-for-loop
    flattened = []
    for row in list_of_lists:
        flattened.extend(row)
    return flattened


class AbstractIdFactory(fact.Factory):
    class Meta:
        abstract = True

    id = fact.LazyAttribute(lambda _: uuid.uuid4().hex)


class AbstractPersonFactory(AbstractIdFactory):
    given_name = fact.Faker('first_name')
    surname = fact.Faker('last_name')


class PersonFactory(AbstractPersonFactory):
    class Meta:
        model = models.Person


class CatFactory(AbstractIdFactory):
    class Meta:
        exclude = ('_owner',)
        model = models.Cat

    _owner = fact.SubFactory(PersonFactory)

    age = fuzzy.FuzzyInteger(0, 20)
    color = fuzzy.FuzzyChoice(['black', 'gray', 'orange', 'other'])
    lives = fuzzy.FuzzyInteger(1, 9)
    name = fact.LazyFunction(petname.name)

    owner_id = fact.SelfAttribute('_owner.id')


class ClinicFactory(AbstractIdFactory):
    class Meta:
        model = models.Clinic

    name = fact.Faker('company')


class VeterinarianFactory(AbstractPersonFactory):
    class Meta:
        exclude = '_clinic'
        model = models.Veterinarian

    _clinic = fact.SubFactory(ClinicFactory)

    clinic_id = fact.SelfAttribute('_clinic.id')
    license_number = fact.Faker('ean8')


class PersonWithCatsFactory(PersonFactory):
    @fact.post_generation
    def post(obj: models.Person, create: bool, extracted: dict[str, Any], **kwargs: Any) -> None:  # noqa: N805
        n_max = extracted or kwargs.get('n_max', 3)
        n = random.randint(1, n_max)
        obj.cats = CatFactory.create_batch(n, _owner=obj)


class ClinicWithVeterinariansFactory(ClinicFactory):
    @fact.post_generation
    def post(obj: models.Clinic, create: bool, extracted: dict[str, Any], **kwargs: Any) -> None:  # noqa: N805
        n_max = extracted or kwargs.get('n_max', 5)
        n = random.randint(1, n_max)
        obj.veterinarians = VeterinarianFactory.create_batch(n, _clinic=obj)


class AppointmentFactory(fact.Factory):
    class Meta:
        exclude = ('_cat', '_clinic', '_owner', '_start', '_veterinarian')
        model = models.Appointment

    _cat = fact.SubFactory(CatFactory)
    _clinic = fact.SubFactory(ClinicFactory)
    _owner = fact.SubFactory(PersonFactory)
    _start = fact.Faker('date_time_this_decade')
    _veterinarian = fact.SubFactory(VeterinarianFactory)

    cat_id = fact.SelfAttribute('_cat.id')
    clinic_id = fact.SelfAttribute('_clinic.id')
    owner_id = fact.SelfAttribute('_owner.id')
    veterinarian_id = fact.SelfAttribute('_veterinarian.id')

    start = fact.LazyAttribute(lambda o: models.round(o._start))


@dataclass
class Dataset:
    appointments: list[models.Appointment]
    cats: list[models.Cat]
    clinics: list[models.Clinic]
    persons: list[models.Person]
    veterinarians: list[models.Veterinarian]


def create_random_appointments(
    obj: Dataset, n: int, person: models.Person
) -> list[models.Appointment]:
    clinic = random.choice(obj.clinics)
    veterinarian = random.choice(clinic.veterinarians)
    return [
        AppointmentFactory(
            _cat=random.choice(person.cats),
            _clinic=clinic,
            _owner=person,
            _veterinarian=veterinarian,
        )
        for _ in range(n)
    ]


class TestDatasetFactory(fact.Factory):
    class Meta:
        model = Dataset

    cats = fact.LazyAttribute(lambda o: flatten(person.cats for person in o.persons))
    clinics = fact.LazyAttribute(lambda _: ClinicWithVeterinariansFactory.create_batch(3))
    persons = fact.LazyAttribute(lambda _: PersonWithCatsFactory.create_batch(50, post__n_max=3))
    veterinarians = fact.LazyAttribute(
        lambda o: flatten(clinic.veterinarians for clinic in o.clinics)
    )

    appointments = fact.LazyAttribute(
        lambda o: flatten(
            create_random_appointments(o, random.randint(1, 4), person) for person in o.persons
        )
    )


class ProdDatasetFactory(fact.Factory):
    class Meta:
        model = Dataset

    cats = fact.LazyAttribute(lambda o: flatten(person.cats for person in o.persons))
    clinics = fact.LazyAttribute(lambda _: ClinicWithVeterinariansFactory.create_batch(300))
    persons = fact.LazyAttribute(
        lambda _: PersonWithCatsFactory.create_batch(100_000, post__n_max=30)
    )
    veterinarians = fact.LazyAttribute(
        lambda o: flatten(clinic.veterinarians for clinic in o.clinics)
    )

    appointments = fact.LazyAttribute(
        lambda o: flatten(
            create_random_appointments(o, random.randint(1, 40), person) for person in o.persons
        )
    )
