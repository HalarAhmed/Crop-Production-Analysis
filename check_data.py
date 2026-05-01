#!/usr/bin/env python3
"""Quick check of what's in the database."""
from backend.database import SessionLocal
from backend.models import MLReadyData
from backend.crud import list_crops

db = SessionLocal()

try:
    crops = list_crops(db)
    print(f"Crops in DB: {crops}\n")
    
    for crop in crops:
        rows = db.query(MLReadyData).filter(MLReadyData.crop_name == crop).all()
        if rows:
            fiscal_years = [r.fiscal_year for r in rows]
            print(f"{crop}: {len(rows)} records")
            print(f"  Range: {fiscal_years[0]} to {fiscal_years[-1]}")
            print(f"  Years: {fiscal_years[:5]}...{fiscal_years[-5:]}\n")
finally:
    db.close()
