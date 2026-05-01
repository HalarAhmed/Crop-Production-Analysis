from __future__ import annotations

from io import StringIO
from pathlib import Path

import psycopg2


BACKUP_FILE = Path("dbms_backup.sql")
DSN = "postgresql://postgres:halar.45@localhost:5432/db"


def extract_copy_blocks(sql_text: str) -> dict[str, str]:
    """
    Extracts COPY ... FROM stdin blocks from pg_dump plain SQL file.
    Returns table_name -> raw tab-separated data block.
    """
    blocks: dict[str, str] = {}
    lines = sql_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("COPY public.") and " FROM stdin;" in line:
            # Example: COPY public.crop (crop_id, crop_name) FROM stdin;
            table = line.split()[1].split(".")[1]
            i += 1
            data_lines: list[str] = []
            while i < len(lines) and lines[i] != "\\.":
                data_lines.append(lines[i])
                i += 1
            blocks[table] = "\n".join(data_lines) + "\n"
        i += 1
    return blocks


def main() -> None:
    sql_text = BACKUP_FILE.read_text(encoding="utf-8", errors="ignore")
    blocks = extract_copy_blocks(sql_text)

    required = ["crop", "year", "productiondata", "weatherdata"]
    missing = [t for t in required if t not in blocks]
    if missing:
        raise RuntimeError(f"Missing COPY blocks for: {missing}")

    conn = psycopg2.connect(DSN)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Respect FK order (children first for truncate)
            cur.execute(
                "TRUNCATE TABLE public.productiondata, public.weatherdata, public.year, public.crop "
                "RESTART IDENTITY CASCADE"
            )

            cur.copy_expert(
                "COPY public.crop (crop_id, crop_name) FROM STDIN",
                StringIO(blocks["crop"]),
            )
            cur.copy_expert(
                "COPY public.year (year_id, fiscal_year) FROM STDIN",
                StringIO(blocks["year"]),
            )
            cur.copy_expert(
                "COPY public.weatherdata (weather_id, year_id, rainfall, avg_temperature) FROM STDIN",
                StringIO(blocks["weatherdata"]),
            )
            cur.copy_expert(
                "COPY public.productiondata (prod_id, crop_id, year_id, area, production, yield) FROM STDIN",
                StringIO(blocks["productiondata"]),
            )

            # Reset sequences to max id
            cur.execute(
                "SELECT setval('public.crop_crop_id_seq', COALESCE((SELECT MAX(crop_id) FROM public.crop), 1), true)"
            )
            cur.execute(
                "SELECT setval('public.year_year_id_seq', COALESCE((SELECT MAX(year_id) FROM public.year), 1), true)"
            )
            cur.execute(
                "SELECT setval('public.weatherdata_weather_id_seq', COALESCE((SELECT MAX(weather_id) FROM public.weatherdata), 1), true)"
            )
            cur.execute(
                "SELECT setval('public.productiondata_prod_id_seq', COALESCE((SELECT MAX(prod_id) FROM public.productiondata), 1), true)"
            )

        conn.commit()
        print("Backup data loaded successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

