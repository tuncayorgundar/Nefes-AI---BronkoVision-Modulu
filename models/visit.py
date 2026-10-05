# prototip/models/visit.py

from dataclasses import dataclass
from datetime import date

@dataclass
class Visit:
    """
    Hasta ziyaret verilerini temsil eden sınıf.
    """
    visit_id: int
    patient_id: int
    visit_date: date
    notes: str