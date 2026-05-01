from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class CropOut(BaseModel):
    crop_name: str


class HistoricalDataPoint(BaseModel):
    fiscal_year: str
    rainfall: float | None
    avg_temperature: float | None
    production: float | None


class HistoricalDataResponse(BaseModel):
    crop_name: str
    start_year: str
    end_year: str
    points: List[HistoricalDataPoint]


class PredictRequest(BaseModel):
    crop_name: str = Field(..., examples=["Wheat"])
    rainfall: float = Field(..., examples=[250.5])
    avg_temperature: float = Field(..., examples=[26.2])


class PredictResponse(BaseModel):
    crop_name: str
    predicted_production: float

