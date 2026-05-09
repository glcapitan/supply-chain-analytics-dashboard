# 02 — Solution Architecture

> *How the data flows from raw sources to executive dashboards.*

## Architecture at a glance

```
┌──────────────┐    ┌─────────┐    ┌─────────┐    ┌──────┐    ┌──────────┐
│ RAW SOURCES  │ →  │ BRONZE  │ →  │ SILVER  │ →  │ GOLD │ →  │ POWER BI │
└──────────────┘    └─────────┘    └─────────┘    └──────┘    └──────────┘
   Sales              Raw,           Cleaned        Dim/Fact      Semantic
   Snapshots          schema-on-     + DQ checks    star-schema   model +
   Movements          read           applied        (Parquet)     dashboards
   Product master                                                 (101 DAX)
   Location master
```

Each layer has a defined contract with the next. Upstream concerns (file formats, naming inconsistencies, type coercion) are resolved before downstream consumers ever see them. By the time data hits Power BI, every column has a known type, every key joins cleanly, and every aggregation is pre-defined.

This is a **medallion lakehouse** pattern — bronze for raw integration, silver for filtering and cleaning, gold for business-level aggregates. The pattern is industry-standard for modern data platforms because it separates the concerns of *capture*, *quality*, and *consumption*.

## Storage layer — DuckDB

For this engagement I used **DuckDB** as the analytical database. DuckDB is an in-process SQL OLAP engine — think SQLite, but columnar and built for analytics. Three reasons it was the right call:

1. **Zero infrastructure.** A single file on disk. No cluster to spin up, no warehouse to provision.
2. **Parquet-native.** DuckDB reads and writes Parquet at high speed, making the gold export step trivial.
3. **Performance at small/mid scale.** 60K+ rows scanned in milliseconds. The 40-SKU dataset fits comfortably in memory.

For larger production workloads this stack would swap to Snowflake, BigQuery, or Databricks — but the medallion pattern and modeling work translate directly.

## Bronze — raw integration

**Purpose:** capture source data with minimal transformation. Schema-on-read, no business logic.

**Tables:**

| Table | Source | Description |
|-------|--------|-------------|
| `bronze__product_master__lite` | Reference file | SKU, name, category, brand, unit_cost |
| `bronze__location_master__lite` | Excel reference | Stores, DCs, web channel — one row per location |
| `bronze__sales_transactions__lite` | Transactional export | Sales events with date as raw string |
| `bronze__inventory_snapshots__lite` | Daily snapshots | On-hand quantities by SKU and location |
| `bronze__inventory_movements__lite` | Event stream | Sale / replenish / adjustment events with from/to locations |

**Design principle:** if the source produces it, bronze stores it as-is. Bronze is the audit trail. Any inconsistency, junk row, or missing value lives here unaltered so it's traceable later.

## Silver — cleaning and validation

**Purpose:** produce trusted tables with enforced types, parsed dates, and validated keys.

**Transformations applied:**

- **Date parsing.** `transaction_date`, `snapshot_date`, `movement_date` parsed from strings to native date types.
- **Dimension uniqueness.** SKU is unique in `silver__product_master__lite`; `location_id` is unique in `silver__location_master__lite`. Duplicates flagged and resolved.
- **Movement type normalization.** All values coerced to `SALE`, `REPLENISH`, or `ADJUSTMENT`. Variants like "sale", "Sales", "SALES" collapsed to canonical form.
- **Range validation.** Quantities checked for reasonableness. Extreme negatives or implausibly large values logged for review.

**Five-check DQ framework run after every Silver build:**

1. Dimension uniqueness — every SKU appears exactly once in the product dimension; every `location_id` exactly once in the location dimension.
2. Key coverage — every SKU referenced in fact tables exists in the product dimension; every location reference resolves.
3. Date parsing success — null rate of parsed date columns is below threshold.
4. Range plausibility — quantity columns within expected bounds.
5. Movement type validity — only the three normalized values appear post-cleaning.

If any check fails, the Silver build is blocked from promoting to Gold. This is the quality gate.

## Gold — business-ready dimensional model

**Purpose:** serve a Kimball-style star schema that Power BI can consume without further transformation.

**Tables produced:**

| Table | Type | Grain |
|-------|------|-------|
| `dim_product` | Dimension | One row per SKU |
| `dim_location` | Dimension | One row per location |
| `dim_date` | Dimension | One row per calendar day |
| `fact_sales` | Fact | One row per sales transaction |
| `fact_inventory_snapshots` | Fact | One row per (date, location, SKU) snapshot |
| `fact_inventory_movements` | Fact | One row per movement event |
| `fact_inventory_exposure` | Fact (derived) | Aggregated overstock / under-stock exposure metrics |

The exposure fact (`gold__adv_fact_inventory_exposure.py`) is the analytical layer where business definitions live — days-of-supply calculations, overstock thresholds, low-stock thresholds, and reorder priority scoring. Pushing these definitions into the gold layer keeps Power BI's DAX layer focused on **measurement and presentation**, not **business logic**.

**Export format:** Parquet. Columnar, compressed, efficient for Power BI's import mode.

## Semantic layer — Power BI

**Purpose:** translate the gold star schema into a measurable, narratable model.

**Model footprint:**

- **14 tables** (dimensions, facts, a `_Measures` table, plus disconnected calculation tables for narrative logic)
- **109 columns** across the facts and dimensions
- **101 DAX measures** organized into display folders:
  - `01 Sales` — revenue, growth, share-of-mix
  - `02 Inventory` — on-hand value, days of supply, low-stock, overstock
  - `03 Stock Health` — exposure tiers, risk scoring
  - `04 Movements` — replenishment vs. sales flow, adjustment counts
  - `10 Narrative` — filter-aware describe-and-prescribe text measures

The narrative folder is the dashboard's signature. Each operational page has a `[Page] Narrative` measure and a `[Page] Action` measure that update dynamically with the user's filter context. When a user narrows to a single category or brand, the text changes to reflect what's specifically true for that selection.

This pattern — **filter-aware narrative bands** — is what makes the dashboard feel intelligent rather than static.

## Visualization — four-page dashboard

| Page | Audience | Purpose |
|------|----------|---------|
| Executive Overview | Leadership, weekly review | Single-screen state of the network |
| Sales Analysis | Merchandising, Commercial | Demand patterns, top performers, slow movers |
| Inventory Analysis | Inventory Planning | Days of supply, overstock risks, capital exposure |
| Movements Analysis | Operations, Logistics | Replenishment vs. sales flow, data quality signals |

Each page follows the same skeleton: filters at top → narrative band → KPI strip → primary chart row → supporting visuals → methodology footer. The visual consistency is intentional — a user who learns one page can navigate any of them.

## Reporting — the human layer

The dashboard surfaces signals; the reports translate them into decisions. Two decks were produced:

- **Executive briefing** (in `reports/`) — the board-level view of the four findings, the financial impact framing, and the 30/60/90 day recommended action roadmap.
- **Case study deck** (in `reports/`) — a portfolio-facing walkthrough of the engagement, the design decisions, and the reframes.

Reporting is not an afterthought. The whole pipeline exists to support these conversations.

---

> Continue: [`03-data-model.md`](03-data-model.md) — star schema details and relationships.
