from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE silver__product_master__lite AS
    WITH base AS (
        SELECT
            UPPER(TRIM(sku))          AS sku,
            TRIM(product_name)        AS product_name,
            UPPER(TRIM(category))     AS category,
            UPPER(TRIM(brand))        AS brand,
            TRY_CAST(unit_cost AS DOUBLE) AS unit_cost
        FROM bronze__product_master__lite
    )
    SELECT
        sku,
        product_name,
        category,
        brand,
        unit_cost
    FROM base;
    """)

    con.close()
    print("✅ Created silver__product_master__lite")


if __name__ == "__main__":
    main()
