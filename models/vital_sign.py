# prototip/models/vital_sign.py

from dataclasses import dataclass

@dataclass
class VitalSign:
    """
    Hasta vital bulgularını temsil eden sınıf.
    """
    vital_sign_id: int
    visit_id: int
    test_name: str
    value: float
    unit: str