# models/patient.py

from dataclasses import dataclass
from datetime import date

@dataclass
class Patient:
    patient_id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    blood_type: str
    phone_number: str
    address: str
    status: str
    visit_dates: list[date]  # Bu parametreyi ekleyin