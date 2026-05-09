# Supply Chain Analytics — End-to-End BI Engagement

> An end-to-end analytics case for an omnichannel retailer: from raw transactional data through a medallion lakehouse, into a Kimball-style analytical model, into four executive-ready Power BI dashboards, and out as a board-level findings deck.
>
> **Headline insight delivered:** the client believed they had a stockout problem. The data showed they had an overstock problem — **60% of SKUs sitting on more than 90 days of cover, ~$95K of working capital trapped in slow-moving inventory, and only 1 SKU at genuine stockout risk.**

---

## Table of Contents

- [Engagement Summary](#engagement-summary)
- [The Business Problem](#the-business-problem)
- [Solution Architecture](#solution-architecture)
- [Key Findings](#key-findings)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [About the Dataset](#about-the-dataset)
- [Project Outputs](#project-outputs)
- [Contact](#contact)

---

## Engagement Summary

**Client profile:** A mid-size omnichannel retailer operating across physical stores, distribution centers, and an e-commerce channel. Assortment of 40 SKUs across 4 categories (Electronics, Grocery, Household, Personal Care) and 4 brands.

**The ask:** Operations suspected stockouts were costing sales. Finance saw inventory growing faster than revenue. Leadership wanted a single source of truth that could resolve the disagreement and surface where capital was actually trapped.

**My role:** End-to-end analytics build — business framing, data ingestion, modeling, KPI design, dashboard delivery, and an executive findings briefing.

**Outcome:** A four-page operational dashboard plus a recommended action register that reframed the leadership conversation from *"stop the stockouts"* to *"recover the trapped capital"* — with $50–70K in identified inventory recovery upside over a 90-day execution horizon.

---

## The Business Problem

> Full write-up: [`docs/01-business-context.md`](docs/01-business-context.md)

The retailer was experiencing the classic omnichannel friction point — multiple teams looking at the same supply chain through different lenses, drawing opposite conclusions:

- **Operations** saw occasional empty shelves and assumed availability was the problem.
- **Finance** saw inventory value rising faster than sales and suspected over-buying.
- **Merchandising** wanted more SKUs added; **Logistics** wanted fewer.

Without a shared analytical baseline, every meeting was a debate. The engagement scope was to build that baseline — and let the data adjudicate.

**The four business questions framing the build:**

1. Where is demand actually concentrated, and is it growing or slowing?
2. Where is inventory positioned relative to demand — under or over?
3. Are replenishment flows keeping pace with sell-through?
4. Where is capital trapped, and what's the recovery path?

---

## Solution Architecture

> Full write-up: [`docs/02-architecture.md`](docs/02-architecture.md)

A four-layer pipeline, built once and refreshed on demand:

```
RAW SOURCES                BRONZE              SILVER              GOLD              POWER BI
─────────────              ──────              ──────              ────              ────────
Sales transactions    →    Raw ingest    →    Cleaned +     →    Star-schema   →    4-page
Inventory snapshots         (as-is,             validated          dim/fact            executive
Inventory movements         schema-on-          (DQ checks         model               dashboard
Product master              read)               applied)
Location master
```

**Bronze** — raw landing zone. Source files ingested with minimal transformation, schema-on-read.

**Silver** — cleaned and validated. Date strings parsed, dimension uniqueness enforced, referential integrity checked, movement types normalized. Five-check DQ framework applied.

**Gold** — business-ready dimensional model. Two dimension tables (`dim_product`, `dim_location`), one date dimension, four fact tables (`fact_sales`, `fact_inventory_snapshots`, `fact_inventory_movements`, `fact_inventory_exposure`). Exported as Parquet.

**Power BI semantic layer** — 14 tables, 109 columns, **101 DAX measures** organized into display folders (Sales / Inventory / Stock Health / Movements / Narrative). Filter-aware narrative measures power the describe-and-prescribe text bands on every page.

---

## Key Findings

The dashboard surfaced four findings that landed in the executive briefing:

### 1. Demand is concentrated and slowing

- Total sales **$715K**, down **-11.3% YoY**
- **Electronics is 42% of revenue** ($304K) — single-category dependency risk
- Best month was 2026-12 at **$61K**; subsequent months show flattening trend

### 2. Inventory is over-positioned across the network

- **161 days of supply** on average — well above healthy 30–45 day range
- **41.6% of SKUs flagged low-stock** by the original logic, but…
- **24 SKUs are overstocked** (>90 days cover) — the bigger and more expensive problem

### 3. Movement flows are functional but data quality is drifting

- **64K movement transactions** processed cleanly (replenish 112K units, sold 111K units)
- Net change of **+826 units** suggests slow accumulation
- **145 adjustment events** flagged for audit — small but non-zero data integrity signal

### 4. The reframe — *"overstock, not stockout"*

Cross-referencing inventory levels against sales velocity revealed that the original "Reorder Priorities" framing had the analytical lens reversed. The dashboard's most-used view was reframed mid-build from **Top 10 Reorder Priorities** to **Top 10 Overstock Risks** — and that reframe became the engagement's primary value driver.

> Full executive briefing in [`reports/`](reports/).

---

## Repository Structure

```
supply-chain-analytics-dashboard/
│
├── README.md                       ← you are here
├── LICENSE                         ← MIT
├── .gitignore
│
├── docs/                           ← analytical narrative
│   ├── 01-business-context.md      ← engagement framing, stakeholders, questions
│   ├── 02-architecture.md          ← medallion pipeline + lakehouse design
│   ├── 03-data-model.md            ← star schema, dim/fact relationships
│   └── 04-dax-highlights.md        ← 6 DAX measures worth the deep-dive
│
├── pipeline/                       ← my pipeline code
│   ├── README.md                   ← layer-by-layer guide
│   ├── bronze/                     ← (ingestion scripts)
│   ├── silver/                     ← (DQ + cleaning scripts)
│   └── gold/
│       ├── export_gold_to_parquet.py
│       └── gold__adv_fact_inventory_exposure.py
│
├── data/
│   └── README.md                   ← data dictionary, source description
│
├── pbix/
│   └── supply_chain_analytics_dshbrdbackup.pbix
│
├── screenshots/
│   ├── 01-executive-overview.png
│   ├── 02-sales-analysis.png
│   ├── 03-inventory-analysis.png
│   └── 04-movements-analysis.png
│
└── reports/
    ├── case-study-deck.pptx        ← portfolio walkthrough
    └── executive-briefing.pptx     ← board-level findings
```

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Storage | DuckDB (development), Parquet (gold export) |
| Pipeline | Python (pandas, pyarrow), SQL (DuckDB dialect) |
| Modeling | Kimball-style star schema |
| Semantic layer | Power BI Desktop, Tabular Object Model (via MCP) |
| Visualization | Power BI (4 pages, 30+ visuals, custom design system) |
| Reporting | PowerPoint (case study + executive briefing decks) |
| Version control | Git + GitHub |

---

## About the Dataset

This is a **portfolio case study using a representative retail dataset** — synthetic but built to mirror the structure, scale, and messiness of real retail supply chain data. The dataset spans **December 2025 through May 2027** and includes:

- ~57K sales transactions across stores, web, and DC channels
- ~17K daily inventory snapshots across 40 SKUs and multiple locations
- ~64K inventory movement events (sales, replenishments, adjustments)

The **analysis, modeling, dashboarding, and storytelling are entirely original work** done end-to-end on this dataset.

---

## Project Outputs

| Output | Location | Audience |
|--------|----------|----------|
| Power BI dashboard (4 pages) | `pbix/` + `screenshots/` | Operations, Inventory Planning, Finance |
| Case study deck | `reports/case-study-deck.pptx` | Hiring managers reviewing portfolio |
| Executive briefing deck | `reports/executive-briefing.pptx` | Stakeholder-level findings presentation |
| Data model documentation | `docs/03-data-model.md` | Technical reviewers |
| DAX highlights | `docs/04-dax-highlights.md` | BI engineers, Power BI peers |

---

## Contact

**Erwin Glenn L. Capitan II**
BI Analyst / Power BI Developer

- LinkedIn: [linkedin.com/in/erwin-glenn-capitan-ii](https://www.linkedin.com/in/erwin-glenn-capitan-ii/)
- Email: glcapitan007@gmail.com
- GitHub: [github.com/glcapitan](https://github.com/glcapitan)

---

*This project was built as a standalone portfolio case demonstrating end-to-end supply chain analytics capability — from business context through dimensional modeling, DAX, dashboard delivery, and executive storytelling.*
