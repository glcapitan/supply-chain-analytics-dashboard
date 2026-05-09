# 01 — Business Context

> *Where the project started, why it mattered, and what the analytics had to support.*

## The retailer

A mid-size omnichannel retailer with three distinct selling channels — physical stores, distribution centers, and an e-commerce web channel. The assortment is narrow and deep: 40 SKUs across four product categories (Electronics, Grocery, Household, Personal Care) and four house brands.

For most of its history the business operated store-first. Inventory was bought centrally, pushed to stores, sold predominantly at brick-and-mortar. Planning cycles were predictable and performance was evaluated at the store level.

In recent years, the company expanded e-commerce capability. That created revenue upside, but introduced complexity the planning function had not yet caught up to:

- Inventory is no longer dedicated to a channel — a unit in a store can fulfill a walk-in, a click-and-collect, or an emergency reallocation.
- Demand signals come from multiple channels with different lead-time expectations.
- Replenishment decisions made for one channel ripple into availability for another.

This is the context the engagement was scoped against.

## The disagreement

Different teams were drawing different conclusions from the same operational reality.

| Team | What they saw | What they believed |
|------|---------------|--------------------|
| Operations | Occasional empty shelves on visible SKUs | "We have a stockout problem — we need to order more aggressively." |
| Finance | Inventory value rising faster than revenue | "We're over-buying. Working capital is being burned." |
| Merchandising | Specific categories selling through fast | "We need to expand the assortment in those categories." |
| Logistics | Replenishment cycles getting tighter | "We can't sustain this cadence. Something has to give." |

Each view was internally coherent. None of them were aligned. Without a shared baseline, every cross-functional meeting devolved into anecdote-trading.

The engagement scope was to build that baseline — and let the data adjudicate.

## The four business questions

I narrowed the engagement to four questions the analytics had to answer cleanly:

### 1. Where is demand actually concentrated, and is it growing or slowing?

Beyond top-line revenue, leadership needed to see **where** demand lived — by category, by SKU, by month — and whether the trend was up, flat, or eroding.

### 2. Where is inventory positioned relative to that demand?

The disagreement between Operations and Finance hinged on this. The dashboard had to show, SKU-by-SKU, whether stock was thin, balanced, or excessive — using a defensible definition (days of supply against trailing demand).

### 3. Are replenishment flows keeping pace with sell-through?

If replenishment was over-running sales, the inventory would build. If under-running, stockouts would emerge. Either signal was actionable; ambiguity was not.

### 4. Where is capital trapped, and what's the recovery path?

Finance needed a quantified answer to "how much money are we sitting on that we could free up?" — at the SKU level, with a recommended action per item.

## What the analytics had to support

These questions translated into specific decision-support requirements:

- **Operations**: weekly visibility into days-of-supply by SKU and location, with explicit thresholds for action.
- **Inventory Planning**: a ranked list of overstocked SKUs by trapped capital, with recommended markdown / clearance / hold actions.
- **Finance**: a working-capital exposure number that could be tracked month-over-month.
- **Executive leadership**: a single-page narrative each week that summarized state and surfaced the one or two issues that needed attention.

The dashboard's **filter-aware narrative bands** — describe-and-prescribe text that updates with every filter change — were designed specifically to serve the executive use case.

## Constraints and trade-offs

A few realities shaped the design:

- **Snapshot vs. transactional measures conflict under multi-year filters.** Days-of-supply calculations break when a multi-year time filter is applied to snapshot data. The model uses two parallel measures — `[Days of Supply (Snapshot)]` for KPI cards and `[Days of Supply (Trend)]` for time-aware trend charts — to preserve correctness on both surfaces.

- **Single-category vs. multi-category narratives.** The narrative bands had to read sensibly when one category was selected and when many were. Conditional logic strips redundant comparison sentences when only one category is in scope.

- **Reorder priority vs. overstock risk.** The original framing (Top 10 Reorder Priorities) was reversed mid-build once the data made the analytical reality clear. The reframe to **Top 10 Overstock Risks** is documented in `04-dax-highlights.md` and was the engagement's largest analytical-judgment moment.

## What this document is not

This is not a description of how the business *should* run, or a prescription for supply chain operating model changes. It's the framing that scoped the analytics build. Operating model decisions are downstream of the visibility this dashboard creates.

The job here was to make the disagreement resolvable — by making the underlying reality visible, measurable, and actionable.

---

> Continue: [`02-architecture.md`](02-architecture.md) — how the medallion pipeline was built.
