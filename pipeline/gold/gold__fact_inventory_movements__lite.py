from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE gold__fact_inventory_movements__lite AS
    SELECT
        movement_id      AS MovementID,
        movement_date    AS MovementDate,
        movement_type    AS MovementType,
        sku              AS ProductSKU,
        from_location_id AS FromLocationID,
        to_location_id   AS ToLocationID,
        qty              AS Quantity
    FROM silver__inventory_movements__lite;
    """)

    con.close()
    print("✅ Created gold__fact_inventory_movements__lite")


if __name__ == "__main__":
    main()
