from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db

router = APIRouter(tags=["historical"])


@router.get("/historical-data")
def get_historical_data(
    crop_name: str = Query(..., min_length=1),
    start_year: str = Query(..., min_length=1),
    end_year: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    points = crud.fetch_historical_data(
        db=db, crop_name=crop_name, start_year=start_year, end_year=end_year
    )
    if not points:
        raise HTTPException(
            status_code=404,
            detail="No historical data found for the given crop/year range.",
        )
    return {
        "crop_name": crop_name,
        "start_year": start_year,
        "end_year": end_year,
        "points": points,
    }

