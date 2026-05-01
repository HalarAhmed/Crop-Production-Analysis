from __future__ import annotations

import re
from typing import Iterable, Optional, Tuple

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session

from .models import Crop, MLReadyData


def list_crops(db: Session) -> list[str]:
    rows = db.execute(select(Crop.crop_name).order_by(Crop.crop_name.asc())).all()
    return [r[0] for r in rows]


def _parse_fiscal_year_start(fiscal_year: str) -> Optional[int]:
    """
    '1980-81' -> 1980
    '2010-11' -> 2010
    Fallback: first 4-digit group if present.
    """
    if not fiscal_year:
        return None
    m = re.search(r"(\d{4})", fiscal_year)
    return int(m.group(1)) if m else None


def get_year_domain_for_crop(db: Session, crop_name: str) -> tuple[list[str], list[int]]:
    """
    Returns:
      - fiscal_year labels in DB order
      - inferred start-year integers (for slider convenience)
    """
    q = (
        select(MLReadyData.fiscal_year)
        .where(MLReadyData.crop_name == crop_name)
        .distinct()
        .order_by(MLReadyData.fiscal_year.asc())
    )
    rows = [r[0] for r in db.execute(q).all()]
    starts: list[int] = []
    for fy in rows:
        y = _parse_fiscal_year_start(fy)
        if y is not None:
            starts.append(y)
    return rows, sorted(set(starts))


def fetch_historical_data(
    db: Session,
    crop_name: str,
    start_year: str,
    end_year: str,
) -> list[dict]:
    """
    start_year/end_year can be:
      - fiscal_year label exactly as stored (e.g. '1980-81')
      - 4-digit start year (e.g. '1980')
    """
    base = (
        select(
            MLReadyData.fiscal_year,
            MLReadyData.rainfall,
            MLReadyData.avg_temperature,
            MLReadyData.production,
        )
        .where(MLReadyData.crop_name == crop_name)
    )

    # If the user passes fiscal_year labels, filter on string range.
    # If they pass 4-digit years, filter on extracted start-year.
    is_numeric_range = start_year.isdigit() and end_year.isdigit()
    if is_numeric_range:
        sy = int(start_year)
        ey = int(end_year)
        fy_start = cast(func.substring(MLReadyData.fiscal_year, 1, 4), Integer)
        base = base.where(fy_start >= sy, fy_start <= ey).order_by(fy_start.asc())
    else:
        base = base.where(
            MLReadyData.fiscal_year >= start_year,
            MLReadyData.fiscal_year <= end_year,
        ).order_by(MLReadyData.fiscal_year.asc())

    rows = db.execute(base).all()
    out: list[dict] = []
    for fiscal_year, rainfall, avg_temperature, production in rows:
        out.append(
            {
                "fiscal_year": fiscal_year,
                "rainfall": float(rainfall) if rainfall is not None else None,
                "avg_temperature": float(avg_temperature) if avg_temperature is not None else None,
                "production": float(production) if production is not None else None,
            }
        )
    return out

