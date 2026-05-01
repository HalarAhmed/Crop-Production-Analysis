from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://postgres:halar.45@localhost:5432/db")

with engine.connect() as conn:
    rows = conn.execute(
        text(
            """
            SELECT fiscal_year, rainfall, avg_temperature, production
            FROM ml_ready_data
            WHERE crop_name = 'Mash'
              AND CAST(SUBSTRING(fiscal_year, 1, 4) AS INT) >= 2012
            ORDER BY CAST(SUBSTRING(fiscal_year, 1, 4) AS INT)
            """
        )
    ).fetchall()

print("rows:", len(rows))
if rows:
    print("first:", rows[0])
    print("last:", rows[-1])
print("null_rows:", sum(1 for r in rows if r[1] is None or r[2] is None or r[3] is None))
