from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE silver__location_master__lite AS
    WITH base AS (
        SELECT
            UPPER(TRIM(location_id))   AS location_id,
            UPPER(TRIM(location_name)) AS location_name,
            UPPER(TRIM(location_type)) AS location_type,
            UPPER(TRIM(region))        AS region
        FROM bronze__location_master__lite
    )
    SELECT
        location_id,
        location_name,
        location_type,
        region
    FROM base;
    """)

    con.close()
    print("✅ Created silver__location_master__lite")


if __name__ == "__main__":
    main()
