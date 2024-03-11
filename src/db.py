"""Define database connections and queries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import models


class Connection:
    """Connect to the database for executing queries."""

    db: Path

    def __init__(self, data_file: str | Path) -> None:
        self.db = Path(data_file)

    def select(self, from_table: str, **where: Any) -> list[dict[str, Any]]:
        """Select records from the given table based on the supplied keyword arguments."""
        with open(self.db) as f:
            data = json.load(f)

        selected: list[dict[str, Any]] = []
        for rec in data[from_table]:
            if all(rec.get(k) == v for k, v in where.items()):
                selected.append(rec)

        return selected

    def get_appointments(self, veterinarian: models.Veterinarian) -> list[models.Appointment]:
        """Return all appointments for the given veterinarian."""
        return [
            models.Appointment(**a)
            for a in self.select('appointments', veterinarian_id=veterinarian.id)
        ]

    def get_cat(self, id: str) -> models.Cat:
        """Return the cat with the given ID."""
        cat = self.select('cats', id=id)[0]
        return models.Cat(**cat)

    def get_clinic(self, name: str) -> models.Clinic:
        """Return the clinic with the given name."""
        clinic = self.select('clinics', name=name)[0]
        return models.Clinic(**clinic)

    def get_veterinarians(self, clinic: models.Clinic) -> list[models.Veterinarian]:
        """Return all veterinarians working at the given clinic."""
        return [models.Veterinarian(**v) for v in self.select('veterinarians', clinic_id=clinic.id)]

    def get_cats_seen_at(self, clinic_name: str) -> list[models.Cat]:
        """Return all cats seen at the given clinic."""
        clinic = self.get_clinic(clinic_name)
        all_cats = self.select('cats', clinic=clinic.id)
        return all_cats
