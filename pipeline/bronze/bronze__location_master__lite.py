from pathlib import Path
import pandas as pd
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    # Correct relative path
    xlsx_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "raw__location_master__lite.xlsx").resolve()

    print("Loading Excel from:", xlsx_path)

    df = pd.read_excel(xlsx_path)

    con = duckdb.connect(str(db_path))
    con.register("tmp_location_master_lite", df)

    con.execute("""
    CREATE OR REPLACE TABLE bronze__location_master__lite AS
    SELECT
        location_id,
        location_name,
        location_type,
        region
    FROM tmp_location_master_lite;
    """)

    con.close()
    print("✅ Created bronze__location_master__lite")


if __name__ == "__main__":
    main()