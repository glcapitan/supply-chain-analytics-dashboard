# Pipeline

> *The medallion lakehouse code that produces the dashboard's input data.*

This folder contains the bronze → silver → gold pipeline that ingests raw retail data and produces the business-ready Parquet tables consumed by the Power BI dashboard.

## Layer overview

```
bronze/   →  Raw integration. Source files captured as-is.
silver/   →  Cleaned and validated. Date parsing, key checks, type enforcement.
gold/     →  Business-ready dimensional model. Star schema exported to Parquet.
```

Full architecture write-up: [`../docs/02-architecture.md`](../docs/02-architecture.md).

## What you'll find here

| Path | Purpose |
|------|---------|
| `bronze/` | Ingestion scripts that load source files into the bronze layer with minimal transformation |
| `silver/` | SQL and Python that clean bronze tables, parse dates, enforce keys, run the five-check DQ framework |
| `gold/export_gold_to_parquet.py` | Reads the gold star schema from DuckDB and writes Parquet files for Power BI consumption |
| `gold/gold__adv_fact_inventory_exposure.py` | Builds the derived `fact_inventory_exposure` table — the analytical layer where days-of-supply, overstock, and reorder logic live |

## Running the pipeline

The pipeline targets a local DuckDB database. To reproduce:

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install duckdb pandas pyarrow openpyxl

# Run the pipeline (in order)
python bronze/<ingestion_script>.py
python silver/<cleaning_script>.py
python gold/gold__adv_fact_inventory_exposure.py
python gold/export_gold_to_parquet.py
```

The final step writes Parquet files to a `gold_exports/` directory. Power BI imports from those files.

## Why DuckDB

DuckDB was chosen over a hosted warehouse for three reasons:

1. **Zero infrastructure** — single file on disk, no cluster to provision.
2. **Parquet-native** — direct read/write of Parquet at high speed.
3. **In-process performance** — 60K+ row scans complete in milliseconds.

For larger workloads the same pipeline pattern translates to Snowflake, BigQuery, or Databricks. The architecture decisions (medallion separation, schema-on-read in bronze, business logic in gold) are platform-independent.

## Note on the dataset

This pipeline runs against a representative retail dataset (40 SKUs, 4 categories, ~57K sales transactions, ~17K inventory snapshots, ~64K movement events) spanning Dec 2025 through May 2027. The raw data files are not included in the repo to keep clone size small — the schema and column descriptions are documented in [`../data/README.md`](../data/README.md).
