# prototip/models/genetic_marker.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class GeneticMarker:
    """
    Genetik Biyobelirteç verilerini temsil eden sınıf.
    """
    marker_list_id: int
    marker_name: str
    result: str
    percentage: Optional[float]
    targeted_therapy: Optional[str]