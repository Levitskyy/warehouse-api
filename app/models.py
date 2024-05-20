from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase): pass

class Coil(Base):
    __tablename__ = 'coils'

    id = Column(Integer, primary_key=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    date_added = Column(DateTime, nullable=False)
    date_removed = Column(DateTime)