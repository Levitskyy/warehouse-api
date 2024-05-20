from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Tuple


class CoilCreate(BaseModel):
    length: float
    weight: float


class Coil(BaseModel):
    id: int
    length: float
    weight: float
    date_added: datetime
    date_removed: Optional[datetime] = None

    class Config:
        orm_mode = True


class CoilFilter(BaseModel):
    id_ranges: Optional[List[Tuple[int, int]]] = None
    length_ranges: Optional[List[Tuple[float, float]]] = None
    weight_ranges: Optional[List[Tuple[float, float]]] = None
    date_added_ranges: Optional[List[Tuple[datetime, datetime]]] = None
    date_removed_ranges: Optional[List[Tuple[datetime, datetime]]] = None
