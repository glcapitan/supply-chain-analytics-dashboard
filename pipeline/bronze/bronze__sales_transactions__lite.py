from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()
    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE bronze__sales_transactions__lite AS
    SELECT
        transaction_id,
        transaction_ts,
        channel,
        location_id,
        sku,
        qty,
        unit_price
    FROM raw__sales_transactions__lite;
    """)

    con.close()
    print("✅ Created bronze__sales_transactions__lite")


if __name__ == "__main__":
    main()
