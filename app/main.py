from datetime import datetime
from typing import Annotated, Dict, List, Tuple
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, crud, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


# Эндпоинт для добавления нового рулона
@app.post("/api/coil", status_code=201)
def create_coil(coil: schemas.CoilCreate, db: Session = Depends(database.get_db)) -> int:
    db_coil = crud.create_coil(db, coil)
    if db_coil is None:
        raise HTTPException(status_code=500, detail="Could not add coil")
    return int(db_coil.id)


# Эндпоинт для удаления рулона по id
@app.delete("/api/coil/{coil_id}", response_model=schemas.Coil)
def delete_coil(coil_id: int, db: Session = Depends(database.get_db)) -> models.Coil:
    db_coil = crud.delete_coil(db, coil_id)
    if db_coil is None:
        raise HTTPException(status_code=404, detail="Coil not found")
    return db_coil


# эндпоинт для получения списка рулонов по наборам фильтров
@app.get("/api/coil", response_model=List[schemas.Coil])
def get_coils(
    id_range: Annotated[Tuple[int, int] | None, Query(min_length=2)] = None,
    weight_range: Annotated[Tuple[float, float] | None, Query(min_length=2)] = None,
    length_range: Annotated[Tuple[float, float] | None, Query(min_length=2)] = None,
    date_added_range: Annotated[Tuple[datetime, datetime] | None, Query(min_length=2)] = None,
    date_removed_range: Annotated[Tuple[datetime, datetime] | None, Query(min_length=2)] = None,
    db: Session = Depends(database.get_db)
) -> List[models.Coil]:
    coils = crud.get_coils_by_filters(
        db=db,
        id_range=id_range,
        weight_range=weight_range,
        length_range=length_range,
        date_added_range=date_added_range,
        date_removed_range=date_removed_range
    )
    return coils


# Эндпоинт для получения статистики за промежуток времени
@app.get("/api/coil/stats")
def get_coil_stats(start_date: datetime, end_date: datetime, db: Session = Depends(database.get_db)) -> Dict:
    stats = crud.get_coil_stats(db, start_date, end_date)
    return stats
