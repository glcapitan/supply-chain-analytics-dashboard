from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE silver__inventory_movements__lite AS
    WITH base AS (
        SELECT
            UPPER(TRIM(movement_id)) AS movement_id,
            movement_date,
            UPPER(TRIM(movement_type)) AS movement_type,
            UPPER(TRIM(sku)) AS sku,
            UPPER(TRIM(from_location_id)) AS from_location_id,
            UPPER(TRIM(to_location_id)) AS to_location_id,
            qty
        FROM bronze__inventory_movements__lite
    )
    SELECT
        movement_id,
        COALESCE(
            TRY_CAST(movement_date AS DATE),
            TRY_STRPTIME(movement_date, '%d/%m/%Y')::DATE
        ) AS movement_date,
        movement_type,
        sku,
        from_location_id,
        to_location_id,
        qty
    FROM base;
    """)

    con.close()
    print("✅ Created silver__inventory_movements__lite")


if __name__ == "__main__":
    main()