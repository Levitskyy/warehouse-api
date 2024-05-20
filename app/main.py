from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import Body, FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, crud, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

# Эндпоинт для добавления нового рулона
@app.post("/api/coil")
def create_coil(coil: schemas.CoilCreate, db: Session = Depends(database.get_db)) -> int:
    db_coil = crud.create_coil(db, coil)
    if db_coil is None:
        raise HTTPException(status_code=500, detail="Could not add coil")
    return db_coil.id

# Эндпоинт для удаления рулона по id
@app.delete("/api/coil/{coil_id}", response_model=schemas.Coil)
def delete_coil(coil_id: int, db: Session = Depends(database.get_db)):
    db_coil = crud.delete_coil(db, coil_id)
    if db_coil is None:
        raise HTTPException(status_code=404, detail="Coil not found")
    return db_coil

# эндпоинт для получения списка рулонов по наборам фильтров
@app.get("/api/coil", response_model=List[schemas.Coil])
def get_coils(filters: schemas.CoilFilter, db: Session = Depends(database.get_db)):
    coils = crud.get_coils_by_filters(
        db=db,
        id_ranges=filters.id_ranges,
        weight_ranges=filters.weight_ranges,
        length_ranges=filters.length_ranges,
        date_added_ranges=filters.date_added_ranges,
        date_removed_ranges=filters.date_removed_ranges
    )
    return coils

# Эндпоинт для получения статистики за промежуток времени
@app.get("/api/coil/stats")
def get_coil_stats(start_date: datetime, end_date: datetime, db: Session = Depends(database.get_db)):
    stats = crud.get_coil_stats(db, start_date, end_date)
    return stats