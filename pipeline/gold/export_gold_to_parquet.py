from pathlib import Path
import duckdb

def main() -> None:
    db_path = Path(r"C:\Users\glcap\Desktop\PortfolioStack\Project case study\supply_chain_analytics.duckdb")
    export_dir = Path(r"C:\Users\glcap\Desktop\PortfolioStack\03_Supply_Chain_Analytics_Light\_Project Assets & Code\gold_exports")
    export_dir.mkdir(exist_ok=True)

    gold_tables = [
        "gold__dim_location__lite",
        "gold__dim_product__lite",
        "gold__fact_sales__lite",
        "gold__fact_inventory_movements__lite",
        "gold__fact_inventory_snapshots__lite",
        "gold__fact_inventory_exposure__lite",
    ]

    con = duckdb.connect(str(db_path))

    for table in gold_tables:
        out_path = export_dir / f"{table}.parquet"
        con.execute(f"COPY {table} TO '{out_path}' (FORMAT PARQUET)")
        print(f"Exported {table} -> {out_path.name}")

    con.close()
    print("\nAll gold tables exported to:", export_dir)

if __name__ == "__main__":
    main()
