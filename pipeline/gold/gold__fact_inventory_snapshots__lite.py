from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE gold__fact_inventory_snapshots__lite AS
    SELECT
        snapshot_date AS SnapshotDate,
        location_id   AS LocationID,
        sku           AS ProductSKU,
        on_hand_qty   AS OnHandQuantity
    FROM silver__inventory_snapshots__lite;
    """)

    con.close()
    print("✅ Created gold__fact_inventory_snapshots__lite")


if __name__ == "__main__":
    main()
