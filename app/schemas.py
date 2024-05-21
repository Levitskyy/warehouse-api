from pydantic import BaseModel
from datetime import datetime, timedelta
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


class CoilStats(BaseModel):
    coils_added: int | None
    coils_removed: int | None
    avg_length: float | None
    avg_weight: float | None
    min_length: float | None
    max_length: float | None
    min_weight: float | None
    max_weight: float | None
    sum_weight: float | None
    min_gap: timedelta | None
    max_gap: timedelta | None
    min_coils_count_date: datetime | None
    max_coils_count_date: datetime | None
    min_sum_weight_date: datetime | None
    max_sum_weight_date: datetime | None
