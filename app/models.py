from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class Coil(Base):
    __tablename__ = 'coils'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_removed: Mapped[Optional[datetime]] = mapped_column(DateTime)
