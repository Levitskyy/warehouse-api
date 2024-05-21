from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Tuple


class CoilCreate(BaseModel):
    length: float
    weight: float


class Coil(BaseModel):
    id: int
    length: float
    weight: float
    date_added: datetime
    date_removed: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True


class CoilFilter(BaseModel):
    id_ranges: Optional[Tuple[int, int]] = None
    length_ranges: Optional[Tuple[float, float]] = None
    weight_ranges: Optional[Tuple[float, float]] = None
    date_added_ranges: Optional[Tuple[datetime, datetime]] = None
    date_removed_ranges: Optional[Tuple[datetime, datetime]] = None
