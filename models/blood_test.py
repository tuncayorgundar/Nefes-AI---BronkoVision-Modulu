# prototip/models/blood_test.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class BloodTest:
    """
    Kan testi sonuçlarını temsil eden sınıf.
    """
    blood_test_list_id: int
    test_name: str
    value: float
    reference_range: str
    status: str
    unit: Optional[str]