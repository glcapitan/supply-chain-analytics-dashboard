from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()
    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE bronze__inventory_snapshots__lite AS
    SELECT
        snapshot_date,
        location_id,
        sku,
        on_hand_qty
    FROM raw__inventory_snapshots__lite;
    """)

    con.close()
    print("✅ Created bronze__inventory_snapshots__lite")


if __name__ == "__main__":
    main()