from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE gold__dim_location__lite AS
    SELECT
        location_id   AS LocationID,
        location_name AS LocationName,
        location_type AS LocationType,
        region        AS Region
    FROM silver__location_master__lite;
    """)

    con.close()
    print("✅ Created gold__dim_location__lite")


if __name__ == "__main__":
    main()
