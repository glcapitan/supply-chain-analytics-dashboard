from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE gold__fact_sales__lite AS
    SELECT
        transaction_id   AS SalesTransactionID,
        CAST(transaction_ts AS DATE) AS SalesDate,
        sku              AS ProductSKU,
        location_id      AS LocationID,
        qty              AS Quantity,
        unit_price       AS UnitPrice
    FROM silver__sales_transactions__lite;
    """)

    con.close()
    print("✅ Created gold__fact_sales__lite")


if __name__ == "__main__":
    main()
