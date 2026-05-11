from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE gold__dim_product__lite AS
    SELECT
        sku          AS ProductSKU,
        product_name AS ProductName,
        category     AS Category,
        brand        AS Brand,
        unit_cost    AS UnitCost
    FROM silver__product_master__lite;
    """)

    con.close()
    print("✅ Created gold__dim_product__lite")


if __name__ == "__main__":
    main()
