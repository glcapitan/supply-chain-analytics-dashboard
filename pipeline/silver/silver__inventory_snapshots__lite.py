from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE silver__inventory_snapshots__lite AS
    WITH base AS (
        SELECT
            snapshot_date,
            UPPER(TRIM(location_id)) AS location_id,
            UPPER(TRIM(sku)) AS sku,
            on_hand_qty
        FROM bronze__inventory_snapshots__lite
    )
    SELECT
        COALESCE(
            TRY_CAST(snapshot_date AS DATE),
            TRY_STRPTIME(snapshot_date, '%d/%m/%Y')::DATE
        ) AS snapshot_date,
        location_id,
        sku,
        on_hand_qty
    FROM base;
    """)

    con.close()
    print("✅ Created silver__inventory_snapshots__lite")


if __name__ == "__main__":
    main()