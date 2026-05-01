from sqlalchemy import create_engine, text

DBS = ["db", "education", "mid", "postgres"]

for db_name in DBS:
    try:
        engine = create_engine(
            f"postgresql+psycopg2://postgres:halar.45@localhost:5432/{db_name}"
        )
        with engine.connect() as conn:
            view_count = conn.execute(
                text(
                    "select count(1) from information_schema.views "
                    "where table_schema='public' and table_name='ml_ready_data'"
                )
            ).scalar()
            table_count = conn.execute(
                text(
                    "select count(1) from information_schema.tables "
                    "where table_schema='public' "
                    "and table_name in ('crop','year','productiondata','weatherdata')"
                )
            ).scalar()
            print(f"{db_name}: view={view_count}, tables={table_count}")
    except Exception as exc:
        print(f"{db_name}: ERR {exc}")
