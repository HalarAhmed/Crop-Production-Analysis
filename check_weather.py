#!/usr/bin/env python3
"""Check for NULL values in weather data."""
from backend.database import SessionLocal, engine
import pandas as pd

# Query the ml_ready_data view for Mash
query = """SELECT crop_name, fiscal_year, production, rainfall, avg_temperature
FROM ml_ready_data WHERE crop_name = 'Mash' ORDER BY fiscal_year;"""

df = pd.read_sql(query, engine)
print(f"Total rows: {len(df)}")
print(f"\nFirst 5:")
print(df.head())
print(f"\nLast 5:")
print(df.tail())
print(f"\nRows with NULL rainfall: {df['rainfall'].isna().sum()}")
print(f"Rows with NULL avg_temperature: {df['avg_temperature'].isna().sum()}")
print(f"Rows with NULL production: {df['production'].isna().sum()}")

# Show any rows with NULLs
nulls = df[df.isna().any(axis=1)]
if len(nulls) > 0:
    print(f"\nRows with NULL values:")
    print(nulls)
