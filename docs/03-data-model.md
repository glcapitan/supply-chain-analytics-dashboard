# 03 — Data Model

> *The dimensional model that sits between the gold lakehouse and Power BI's measurement layer.*

## Design choice — Kimball star schema

The semantic layer is a classic Kimball star schema: dimension tables on the perimeter, three fact tables sharing common dimensions, surrogate-key relationships connecting them. No snowflaking, no fact-to-fact joins, no role-playing dimensions.

This is a deliberate choice. Star schemas are not the newest pattern, but for a Power BI engagement that needs to be readable, performant, and intuitive to a future maintainer, they remain the right call. Three reasons:

1. **DAX engines are optimized for star schemas.** Filter propagation, relationship traversal, and `CALCULATE` semantics all assume this shape. Deviate, and performance degrades sharply.
2. **Business users can reason about it.** A dimension is a "thing you slice by." A fact is "an event you measure." Anyone who has used a pivot table understands this implicitly.
3. **Future analysts can extend it.** Adding a new fact (e.g., `fact_returns`) or a new dimension (e.g., `dim_supplier`) is a low-risk operation when the schema is well-shaped to begin with.

## Schema at a glance

```
                              ┌──────────────┐
                              │   dim_date   │
                              └──────┬───────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
   ┌───────▼────────┐   ┌────────────▼───────────┐   ┌─────────▼────────────┐
   │  fact_sales    │   │ fact_inventory_        │   │ fact_inventory_      │
   │                │   │    snapshots           │   │    movements         │
   └───┬────────┬───┘   └─────┬───────────┬──────┘   └────┬────────────┬────┘
       │        │             │           │               │            │
       │        │             │           │               │            │
   ┌───▼────────▼──┐     ┌────▼───────────▼──┐     ┌──────▼────────────▼─┐
   │  dim_product  │◀────┤   dim_location    │────▶│   (shared dims)     │
   └───────────────┘     └───────────────────┘     └─────────────────────┘
```

The three primary fact tables share three dimensions: date, product, location. Cross-fact analysis (e.g., "join sales velocity to inventory levels") is handled in DAX measures, not via fact-to-fact relationships — which keeps the model clean and avoids many-to-many traps.

## Model footprint

| Element | Count |
|---------|-------|
| Tables (total) | 14 |
| Columns (total) | 109 |
| DAX measures | 101 |
| Dimension tables | 3 core + supporting helpers |
| Fact tables | 3 primary |
| Measure organization | 5 display folders + utility folders |

## Dimension tables

### `dim_product`

**Grain:** one row per SKU. Approximately **40 rows.**

```
ProductSKU       (PK)
ProductName
Category
Brand
UnitCost
```

The product dimension covers 40 SKUs across **4 categories** — ELECTRONICS, GROCERY, HOUSEHOLD, PERSONAL CARE — and **4 house brands** — EIRA, FJORD, NORDMARK, POLAR. Category and brand are the dashboard's primary segmentation axes; most pages support both as filter dimensions. `UnitCost` powers all inventory value and trapped-capital calculations.

### `dim_location`

**Grain:** one row per location. Approximately **5 rows.**

```
LocationID       (PK)
LocationName
LocationType
Region
```

Locations span three channel types — **stores, distribution centers, and the e-commerce web channel** — modeled as a single dimension rather than separate ones because they all serve as origin/destination points for the same inventory events. `LocationType` is the column that drives channel-level analysis throughout the dashboard.

### `dim_date`

**Grain:** one row per calendar day. Approximately **550 rows** covering **December 2025 through May 2027.**

```
Date             (PK)
Year
Month (Short)
Year-Month
Year-Month Key
```

The date dimension is the most over-engineered table in the model on purpose: most analytical questions are time-shaped, and a thin date dimension forces complex DAX everywhere else.

A small but important detail — `Year-Month` is a text column (e.g., `"2026-01"`) used as a display label, while `Year-Month Key` is an integer (e.g., `202601`) used as the sort-by column. Power BI's `Sort by column` setting points the text label at the integer key, guaranteeing correct chronological ordering even across decade boundaries. Without this, a chart could happily display 2026-01 after 2025-12 alphabetically — but break entirely if the data ever extended to 2030.

## Fact tables

### `fact_sales`

**Grain:** one row per sales transaction (line-item level). Volume: **~57,000 rows.**

```
SaleID
SaleDate         → dim_date[Date]
ProductSKU       → dim_product[ProductSKU]
LocationID       → dim_location[LocationID]
Quantity
UnitPrice
Revenue          (= Quantity × UnitPrice)
```

Most sales-side measures (Total Sales, Sales Share %, Top Performer rankings, MoM, YTD vs PYTD) aggregate from this table.

### `fact_inventory_snapshots`

**Grain:** one row per (SnapshotDate, LocationID, ProductSKU). Volume: **~17,000 rows.**

```
SnapshotID
SnapshotDate     → dim_date[Date]
ProductSKU       → dim_product[ProductSKU]
LocationID       → dim_location[LocationID]
OnHandQty
```

This is the source for all point-in-time inventory KPIs: Total On-Hand Value, Inventory Units, Days of Supply (snapshot variant), Low Stock %, Overstocked SKUs.

The snapshot pattern requires defensive measure design when interacting with date filters — covered in detail in [`04-dax-highlights.md`](04-dax-highlights.md), measure #2.

### `fact_inventory_movements`

**Grain:** one row per movement event. Volume: **~64,000 rows** covering sales-driven outflows, replenishment inflows, and adjustments.

```
MovementID
MovementDate     → dim_date[Date]
ProductSKU       → dim_product[ProductSKU]
LocationID       → dim_location[LocationID]
MovementType     (SALE | REPLENISH | ADJUSTMENT)
Quantity
```

The Movements page lives entirely off this table. It feeds the Replenishment vs. Sales Flow chart, Net Change by Category, Movement Mix, and the Risk Summary action register.

The 145 adjustment events flagged in the dashboard's Risk Summary are filtered from here — adjustments are a small percentage of total movements, but their existence is a data-quality signal worth surfacing.

## Helper tables

Three supporting tables sit alongside the dimensions and facts:

### `Stock Tier Categories`

A 4-row helper that drives the SKU Count by Tier chart on the Inventory page. Tiers — **Critical / Watch / Healthy / Overstocked** — each have a sort order and a color hex code, which lets the chart's bar coloring stay synchronized with the tier definition without hardcoding colors in the visual.

### `Risk Summary`

A 4-row `DATATABLE` driving the Movement Risk Summary visual on the Movements page:

```dax
Risk Summary =
DATATABLE(
    "Sort Order", INTEGER,
    "Signal", STRING,
    {
        {1, "Net Change"},
        {2, "Adjustment Events"},
        {3, "Top Activity Category"},
        {4, "Top SKU Variance"}
    }
)
```

The Risk Summary card is the dashboard's most differentiated visual — a static four-row table populated entirely by measures. The narrative measures (`[Risk Finding]`, `[Risk Action]`, `[Risk Severity Color]`) read the model state on every refresh and re-narrate the four signals dynamically. Adding a fifth signal is a one-row insert here, not a re-build.

### `_Measures`

A measure-only table — no data rows — that holds all 101 DAX measures organized into display folders. Covered below.

## Relationships

All relationships are **single-direction many-to-one** from fact to dimension. Bidirectional filtering is avoided — it creates ambiguity for DAX, hurts performance, and rarely produces results worth the cost. Cross-fact analysis is handled in measures, not in relationships.

| From | To | Cardinality | Direction | Active |
|---|---|---|---|---|
| fact_sales[ProductSKU] | dim_product[ProductSKU] | M:1 | Single | Yes |
| fact_sales[LocationID] | dim_location[LocationID] | M:1 | Single | Yes |
| fact_sales[SaleDate] | dim_date[Date] | M:1 | Single | Yes |
| fact_inventory_snapshots[ProductSKU] | dim_product[ProductSKU] | M:1 | Single | Yes |
| fact_inventory_snapshots[LocationID] | dim_location[LocationID] | M:1 | Single | Yes |
| fact_inventory_snapshots[SnapshotDate] | dim_date[Date] | M:1 | Single | Yes |
| fact_inventory_movements[ProductSKU] | dim_product[ProductSKU] | M:1 | Single | Yes |
| fact_inventory_movements[LocationID] | dim_location[LocationID] | M:1 | Single | Yes |
| fact_inventory_movements[MovementDate] | dim_date[Date] | M:1 | Single | Yes |

## The `_Measures` table

All 101 DAX measures live in a single dedicated table called `_Measures`. The table itself contains no data — it's a "measure home" that keeps the field list organized in Power BI.

Measures are organized into **display folders**:

| Folder | Approximate count | Purpose |
|--------|-------------------|---------|
| `01 Sales` | ~25 | Revenue, growth, share-of-mix, ranking |
| `02 Inventory` | ~15 | On-hand value, units, days of supply, stock health flags |
| `03 Stock Health` | ~30 | Exposure tiers, risk scoring, action recommendations |
| `04 Movements` | ~10 | Replenishment, sales issues, adjustments, net change |
| `10 Narrative` | 8 | Filter-aware describe-and-prescribe text + Risk Summary drivers |
| Utility folders | (remainder) | Internal helpers, parameter-driven measures |

The numeric prefixes force a stable display order in the field list — folders sort alphanumerically, so `01` always appears before `10`. This is invisible in the rendered model but makes navigation linear during development. Senior Power BI developers use this pattern by default.

The narrative folder is the dashboard's signature, covered in detail in [`04-dax-highlights.md`](04-dax-highlights.md).

## Key modeling decisions

A few choices worth flagging for anyone reading the model in the future.

### 1. Three separate fact tables, not one combined "events" table

Sales, snapshots, and movements live at fundamentally different grains:

- **Sales:** transaction-level — one customer purchase per row
- **Snapshots:** point-in-time — inventory position at end-of-period
- **Movements:** event-level — every stock change, regardless of cause

Combining them into a single fact table would force false equivalence between events that are not equivalent. A star schema with shared dimensions handles the difference cleanly and lets each fact be measured on its own terms.

### 2. Three Days of Supply variants for three different surfaces

`Days of Supply` is the model's most-used analytical metric, and it has **three** distinct measure variants because no single one serves every visual correctly:

- **`Days of Supply (Snapshot)`** — uses latest inventory ÷ trailing 30-day sales. *Ignores time filters.* Used on KPI cards where "right now" is the point of interest.
- **`Days of Supply (Current)`** — uses current inventory ÷ average daily sales. Originally intended for SKU-level cards, but breaks under date filters and was deprecated in most surfaces. Retained for backward compatibility on a few SKU-level visuals.
- **`Days of Supply (Trend)`** — uses average inventory in period ÷ daily sales rate. *Reacts to time filters.* Used on the trend chart where DoS needs to vary monthly.

Choosing the right variant per visual is critical. Using the snapshot version on a trend chart produces a flat line; using the trend version on a KPI card produces a number that doesn't match what the user expects. The variant choice is documented inline in each measure's description.

### 3. Risk Summary as a calculated table, not hardcoded text

The Movement Risk Summary visual could have been built as static text in the .pbix. It wasn't — it's a 4-row `DATATABLE` populated by measures that re-read the model on every refresh.

This choice does three things:

- Keeps the visual **data-driven** — the findings update automatically as data changes
- Keeps the visual **filter-aware** — applying a category filter changes what the action register says
- Allows new signals to be added by inserting one row, rather than rebuilding the visual

It's the difference between a *report* and a *system*.

### 4. No snowflaking on brand

Brand could theoretically be its own dimension (`dim_brand`), with `dim_product` referencing it via a foreign key. With only 4 brands and a clean 1-to-many relationship, flattening brand into `dim_product` is simpler, faster, and equally maintainable.

### 5. Single-direction relationships only

No bidirectional filtering anywhere in the model. Bidirectional filters introduce DAX ambiguity, hurt query performance, and rarely produce results that couldn't be achieved with explicit `CALCULATE` patterns instead. Cross-fact analysis (e.g., joining sales velocity to current stock) is done in measures.

## Grain and cardinality notes

| Table | Grain | Approximate row count |
|---|---|---|
| dim_product | ProductSKU | 40 |
| dim_location | LocationID | 5 |
| dim_date | Date | ~550 |
| Stock Tier Categories | Tier | 4 |
| Risk Summary | Sort Order | 4 |
| fact_sales | SaleID | ~57,000 |
| fact_inventory_snapshots | SnapshotID | ~17,000 |
| fact_inventory_movements | MovementID | ~64,000 |

At this volume the model fits comfortably in import mode; no partitioning or DirectQuery is required. Refresh time is sub-second on a modern laptop.

## Refresh considerations

This is a portfolio dataset and runs without a refresh schedule. In a production deployment, the typical refresh cadence would be:

- **Sales:** hourly or daily, depending on operational tempo
- **Inventory snapshots:** daily, end-of-day after stores close
- **Inventory movements:** real-time or near-real-time, with a daily roll-up if real-time isn't feasible

The dashboard is designed to be refresh-cadence-agnostic — measures use `MAX([SnapshotDate])` rather than hard-coded dates, so a refresh dropping in new data updates every visual automatically without DAX changes.

---

> Continue: [`04-dax-highlights.md`](04-dax-highlights.md) — six DAX measures worth a closer look.
> Back to: [`README.md`](../README.md)
