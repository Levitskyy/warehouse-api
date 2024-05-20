from typing import List, Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timezone

def create_coil(db: Session, coil: schemas.CoilCreate) -> models.Coil:
    db_coil = models.Coil(
        length=coil.length,
        weight=coil.weight,
        date_added=datetime.now(timezone.utc)
    )
    db.add(db_coil)
    db.commit()
    db.refresh(db_coil)
    return db_coil

def delete_coil(db: Session, coil_id: int) -> models.Coil:
    db_coil = db.query(models.Coil).filter(models.Coil.id == coil_id).first()
    if db_coil:
        db_coil.date_removed = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_coil)
    return db_coil

def filter_by_ranges(query, column, ranges: Optional[List[Tuple]]):
    if ranges:
        filters = [column.between(start, end) for start, end in ranges]
        query = query.filter(or_(*filters))
    return query

def get_coils_by_filters(
        db: Session,
        id_ranges: Optional[List[Tuple[int, int]]] = None,
        length_ranges: Optional[List[Tuple[float, float]]] = None,
        weight_ranges: Optional[List[Tuple[float, float]]] = None,
        date_added_ranges: Optional[List[Tuple[datetime, datetime]]] = None,
        date_removed_ranges: Optional[List[Tuple[datetime, datetime]]] = None,
) -> List[models.Coil]:
    query = db.query(models.Coil)

    query = filter_by_ranges(query, models.Coil.id, id_ranges)
    query = filter_by_ranges(query, models.Coil.length, length_ranges)
    query = filter_by_ranges(query, models.Coil.weight, weight_ranges)
    query = filter_by_ranges(query, models.Coil.date_added, date_added_ranges)
    query = filter_by_ranges(query, models.Coil.date_removed, date_removed_ranges)

    return query.all()

def get_coil_stats(db: Session, start_date: datetime, end_date: datetime):
    coils_added = db.query(models.Coil).filter(models.Coil.date_added.between(start_date, end_date)).count()
    coils_removed = db.query(models.Coil).filter(models.Coil.date_removed.between(start_date, end_date)).count()

    coils_in_time_range = db.query(models.Coil).filter(models.Coil.date_added <= end_date, or_(models.Coil.date_removed >= start_date, models.Coil.date_removed == None)).all()

    sum_length = sum(coil.length for coil in coils_in_time_range)
    sum_weight = sum(coil.weight for coil in coils_in_time_range)

    avg_length = sum_length / len(coils_in_time_range) if coils_in_time_range else 0
    avg_weight = sum_weight / len(coils_in_time_range) if coils_in_time_range else 0

    min_length = min(coil.length for coil in coils_in_time_range) if coils_in_time_range else 0
    max_length = max(coil.length for coil in coils_in_time_range) if coils_in_time_range else 0
    min_weight = min(coil.weight for coil in coils_in_time_range) if coils_in_time_range else 0
    max_weight = max(coil.weight for coil in coils_in_time_range) if coils_in_time_range else 0

    removed_coils = [coil for coil in coils_in_time_range if coil.date_removed != None]

    min_gap = min((coil.date_removed - coil.date_added).days for coil in removed_coils) if removed_coils else 0
    max_gap = max((coil.date_removed - coil.date_added).days for coil in removed_coils) if removed_coils else 0

    return {
        'coils_added': coils_added,
        'coils_removed': coils_removed,
        'avg_length': avg_length,
        'avg_weight': avg_weight,
        'min_length': min_length,
        'max_length': max_length,
        'min_weight': min_weight,
        'max_weight': max_weight,
        'min_gap': min_gap,
        'max_gap': max_gap
    }
    