from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .database import Base


class Crop(Base):
    __tablename__ = "crop"

    crop_id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), nullable=False, unique=True, index=True)

    production_rows = relationship("ProductionData", back_populates="crop")


class Year(Base):
    __tablename__ = "year"

    year_id = Column(Integer, primary_key=True, index=True)
    fiscal_year = Column(String(20), nullable=False, unique=True, index=True)

    production_rows = relationship("ProductionData", back_populates="year")
    weather_rows = relationship("WeatherData", back_populates="year")


class ProductionData(Base):
    __tablename__ = "productiondata"

    prod_id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop.crop_id"))
    year_id = Column(Integer, ForeignKey("year.year_id"))

    area = Column(Numeric)
    production = Column(Numeric)
    yield_ = Column("yield", Numeric)

    crop = relationship("Crop", back_populates="production_rows")
    year = relationship("Year", back_populates="production_rows")


class WeatherData(Base):
    __tablename__ = "weatherdata"

    weather_id = Column(Integer, primary_key=True, index=True)
    year_id = Column(Integer, ForeignKey("year.year_id"))

    rainfall = Column(Numeric)
    avg_temperature = Column(Numeric)

    year = relationship("Year", back_populates="weather_rows")


# View (read-only mapping)
class MLReadyData(Base):
    __tablename__ = "ml_ready_data"

    # Views often lack a primary key; for ORM use we provide a composite-ish surrogate.
    # This is safe for SELECTs; we never write to this.
    crop_name = Column(String(100), primary_key=True)
    fiscal_year = Column(String(20), primary_key=True)

    area = Column(Numeric)
    production = Column(Numeric)
    yield_ = Column("yield", Numeric)
    rainfall = Column(Numeric)
    avg_temperature = Column(Numeric)

