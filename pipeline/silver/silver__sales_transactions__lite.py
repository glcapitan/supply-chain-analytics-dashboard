from pathlib import Path
import duckdb


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    db_path = (script_dir / ".." / ".." / ".." / ".." / "Project case study" / "supply_chain_analytics.duckdb").resolve()

    con = duckdb.connect(str(db_path))

    con.execute("""
    CREATE OR REPLACE TABLE silver__sales_transactions__lite AS
    WITH base AS (
        SELECT
            UPPER(TRIM(transaction_id)) AS transaction_id,
            transaction_ts,
            UPPER(TRIM(channel))        AS channel,
            UPPER(TRIM(location_id))    AS location_id,
            UPPER(TRIM(sku))            AS sku,
            qty,
            TRY_CAST(unit_price AS DOUBLE) AS unit_price
        FROM bronze__sales_transactions__lite
    )
    SELECT
        transaction_id,
        COALESCE(
            TRY_CAST(transaction_ts AS TIMESTAMP),
            TRY_STRPTIME(transaction_ts::VARCHAR, '%d/%m/%Y %H:%M:%S')
        ) AS transaction_ts,
        channel,
        location_id,
        sku,
        qty,
        unit_price
    FROM base;
    """)

    con.close()
    print("✅ Created silver__sales_transactions__lite")


if __name__ == "__main__":
    main()
