from typing import Generator, List, Optional, Tuple
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date, datetime, time, timedelta, timezone


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


def delete_coil(db: Session, coil_id: int) -> Optional[models.Coil]:
    db_coil = db.get(models.Coil, coil_id)
    if db_coil:
        if db_coil.date_removed is None:
            db_coil.date_removed = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_coil)
    return db_coil


def get_coils_by_filters(
        db: Session,
        id_range: Optional[Tuple[int, int]] = None,
        length_range: Optional[Tuple[float, float]] = None,
        weight_range: Optional[Tuple[float, float]] = None,
        date_added_range: Optional[Tuple[datetime, datetime]] = None,
        date_removed_range: Optional[Tuple[datetime, datetime]] = None,
) -> List[models.Coil]:
    query = select(models.Coil)
    if id_range:
        query = query.where(models.Coil.id.between(id_range[0], id_range[1]))
    if length_range:
        query = query.where(models.Coil.length.between(length_range[0], length_range[1]))
    if weight_range:
        query = query.where(models.Coil.weight.between(weight_range[0], weight_range[1]))
    if date_added_range:
        query = query.where(models.Coil.date_added.between(date_added_range[0], date_added_range[1]))
    if date_removed_range:
        query = query.where(models.Coil.date_removed.between(date_removed_range[0], date_removed_range[1]))
    result = db.execute(query)
    return list(result.scalars().all())


# Генератор для прохода по дням
def dateranges(start_date: date, end_date: date) -> Generator[Tuple[datetime, datetime], None, None]:
    for n in range(int((end_date - start_date).days)):
        cur_day = datetime.combine(start_date + timedelta(days=n), time(0, 0, 0, 0))
        next_day = cur_day + timedelta(days=1)
        yield cur_day, next_day


def get_coil_stats(db: Session, start_date: date, end_date: date) -> schemas.CoilStats | None:
    if start_date > datetime.now(timezone.utc).date():
        return None
    coils_added = db.execute(
        select(func.count(models.Coil.id)).where(models.Coil.date_added.between(start_date, end_date))
    ).scalar_one()

    coils_removed = db.execute(
        select(func.count(models.Coil.id)).where(models.Coil.date_removed.between(start_date, end_date))
    ).scalar_one()

    coils_in_time_range = db.execute(
        select(models.Coil).where(
            models.Coil.date_added <= end_date,
            or_(models.Coil.date_removed >= start_date, models.Coil.date_removed.is_(None))
        )
    ).scalars().all()

    sum_length = sum(coil.length for coil in coils_in_time_range)
    sum_weight = sum(coil.weight for coil in coils_in_time_range)

    avg_length = sum_length / len(coils_in_time_range) if coils_in_time_range else None
    avg_weight = sum_weight / len(coils_in_time_range) if coils_in_time_range else None

    min_length = min(coil.length for coil in coils_in_time_range) if coils_in_time_range else None
    max_length = max(coil.length for coil in coils_in_time_range) if coils_in_time_range else None
    min_weight = min(coil.weight for coil in coils_in_time_range) if coils_in_time_range else None
    max_weight = max(coil.weight for coil in coils_in_time_range) if coils_in_time_range else None

    min_coils_count = None
    max_coils_count = None
    min_coils_count_date = None
    max_coils_count_date = None

    min_sum_weight = None
    max_sum_weight = None
    min_sum_weight_date = None
    max_sum_weight_date = None

    for cur_day, next_day in dateranges(start_date, end_date):
        day_coils = db.execute(
            select(models.Coil).where(
                models.Coil.date_added <= cur_day,
                or_(models.Coil.date_removed.is_(None), models.Coil.date_removed >= next_day)
            )
        ).scalars().all()

        coils_count = len(day_coils)
        coils_sum_weight = sum(coil.weight for coil in day_coils)

        if min_coils_count is None or coils_count < min_coils_count:
            min_coils_count = coils_count
            min_coils_count_date = cur_day
        if max_coils_count is None or coils_count > max_coils_count:
            max_coils_count = coils_count
            max_coils_count_date = cur_day

        if min_sum_weight is None or coils_sum_weight < min_sum_weight:
            min_sum_weight = coils_sum_weight
            min_sum_weight_date = cur_day
        if max_sum_weight is None or coils_sum_weight > max_sum_weight:
            max_sum_weight = coils_sum_weight
            max_sum_weight_date = cur_day

    removed_coils = [coil for coil in coils_in_time_range if coil.date_removed is not None]

    if removed_coils:
        min_gap = min((coil.date_removed - coil.date_added) for coil in removed_coils if coil.date_removed)
        max_gap = max((coil.date_removed - coil.date_added) for coil in removed_coils if coil.date_removed)
    else:
        min_gap = None
        max_gap = None

    return schemas.CoilStats(
        coils_added=coils_added,
        coils_removed=coils_removed,
        avg_length=avg_length,
        avg_weight=avg_weight,
        min_length=min_length,
        max_length=max_length,
        min_weight=min_weight,
        max_weight=max_weight,
        sum_weight=sum_weight,
        min_gap=min_gap,
        max_gap=max_gap,
        min_coils_count_date=min_coils_count_date,
        max_coils_count_date=max_coils_count_date,
        min_sum_weight_date=min_sum_weight_date,
        max_sum_weight_date=max_sum_weight_date
    )
