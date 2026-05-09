# 04 — DAX Highlights

> *Six measures from the model worth a closer look — selected for the analytical judgment they encode, not just the technical pattern.*

The full model contains 101 measures. This document covers the six that most clearly demonstrate the project's analytical signature: filter-aware narration, defensive coding under date filters, and the analytical reframes that shifted how the data tells its story.

---

## 1. Filter-aware narrative bands

> **Pattern:** dynamically generated describe-and-prescribe text that updates as filters change.

The describe-and-prescribe narrative band is the dashboard's signature design element. Every operational page has two measures behind it — one that *describes* what's true given current filter context, and one that *prescribes* what should happen next.

**Example: `[Inventory Action]` (simplified)**

```dax
Inventory Action =
VAR _DoS = [Days of Supply (Snapshot)]
VAR _OverstockCount = [Overstocked SKUs]
VAR _LowStockPct = [Low Stock %]
RETURN
SWITCH(
    TRUE(),
    _DoS > 180,             "🔴 URGENT ▶ Initiate clearance on top overstock risks",
    _DoS > 120,             "🟠 Investigate ▶ Review buying cadence for slow categories",
    _OverstockCount >= 20,  "🟡 Rebalance ▶ Markdown plan for >90-day cover SKUs",
    _LowStockPct > 50,      "🟡 Stock-up ▶ Replenishment review for thin SKUs",
    _DoS < 30,              "🟢 Monitor ▶ Stock thinning — watch availability",
                            "🟢 On track ▶ Inventory positioning healthy"
)
```

**Why this matters:** the action register isn't hardcoded. It reads the model state, applies graded thresholds, and surfaces the right next step. When the user filters to a single category, the action updates to reflect what's true for that category.

---

## 2. Defensive snapshot measures under date filters

> **Pattern:** snapshot-based KPIs that don't break when the user applies a multi-year time filter.

Snapshot measures (point-in-time inventory levels) and transactional measures (sales over a period) have a fundamental conflict — if you put a multi-year filter on the page, the snapshot returns blank because no single date falls within the entire range.

**Example: `[Days of Supply (Snapshot)]`**

```dax
Days of Supply (Snapshot) =
VAR _LatestSnapshotDate = CALCULATE(
    MAX(fact_inventory_snapshots[snapshot_date]),
    REMOVEFILTERS(dim_date)
)
VAR _OnHand = CALCULATE(
    SUM(fact_inventory_snapshots[on_hand_qty]),
    fact_inventory_snapshots[snapshot_date] = _LatestSnapshotDate
)
VAR _DailyDemand = DIVIDE([Trailing 90-Day Sales Qty], 90)
RETURN
DIVIDE(_OnHand, _DailyDemand)
```

**Why this matters:** `REMOVEFILTERS(dim_date)` lets the snapshot ignore the page-level date filter and always pick up the most recent snapshot. The user's date filter still applies to the demand calculation in the denominator, so the resulting DoS number remains meaningful — it's "today's stock against the demand pace from your selected window."

The companion measure `[Days of Supply (Trend)]` does the opposite — it respects the date filter, used in the time-aware trend chart. Two measures, two surfaces, no breakage.

---

## 3. Best Month — guarding against null Year-Month rows

> **Pattern:** TOPN with a defensive blank filter to prevent phantom rows from polluting results.

A subtle bug surfaced during portfolio review: `[Best Month Sales]` was returning a phantom $947K. The root cause was a null `Year-Month` row in the date dimension that aggregated all sales without a parsed transaction date.

**Fix:**

```dax
Best Month =
CALCULATE(
    SELECTCOLUMNS(
        TOPN(1,
            FILTER(
                VALUES(dim_date[Year-Month]),
                NOT ISBLANK(dim_date[Year-Month])
            ),
            [Total Sales],
            DESC
        ),
        "BestMonth", dim_date[Year-Month]
    ),
    ALLSELECTED(dim_product)
)
```

**Why this matters:** two defensive patterns at once. The `NOT ISBLANK` filter excludes the null row that was inflating the result. The `CALCULATE(SELECTCOLUMNS(TOPN(...)))` wrapper resolves the row-context-on-iteration issue that breaks naked `TOPN` returns when used in a card visual. After the fix, `[Best Month Sales]` returned the correct $60,552.

---

## 4. The Reframe — Top 10 Reorder Priorities → Top 10 Overstock Risks

> **Pattern:** ranked SKU table where the *direction of the rank* embodies the analytical reframe.

The Inventory page originally had a "Top 10 Reorder Priorities" table — SKUs at risk of stockout, ranked by urgency. As the data came together it became clear the analytical reality was the opposite. Stockout risk affected one SKU. Overstock risk affected twenty-four.

The table was reframed:

```dax
Reorder Priority Score =
VAR _DoS = [Days of Supply (Snapshot)]
VAR _Velocity = [Trailing 30-Day Sales Qty]
RETURN
DIVIDE(_Velocity, _DoS + 1)

Overstock Score =
VAR _OnHandValue = [Total On-Hand Value]
VAR _DoS = [Days of Supply (Snapshot)]
VAR _Velocity = [Trailing 30-Day Sales Qty]
RETURN
IF(
    _DoS > 90 && _Velocity > 0,
    _OnHandValue * (_DoS / 90),
    BLANK()
)
```

**Why this matters:** the new measure ranks SKUs by **trapped capital weighted by overstock severity**. A $20K SKU sitting on 200 days of cover ranks higher than a $5K SKU sitting on 100 days. This is the question the business actually needed answered — *"where should we recover capital first?"* — and it didn't exist until the reframe.

This is the engagement's clearest demonstration of analytical judgment over procedural execution.

---

## 5. Movement flow severity coloring

> **Pattern:** measure that returns a color hex code based on data-driven severity tiers.

The Movements page uses bar chart coloring to encode severity at a glance. Net change by category gets colored red / amber / green based on the magnitude relative to a normal-flow baseline.

**Example:**

```dax
Net Change Severity Color =
VAR _NetChange = [Net Inventory Change]
VAR _AbsChange = ABS(_NetChange)
RETURN
SWITCH(
    TRUE(),
    _AbsChange > 500,  "#D64545",  // red — significant accumulation or drawdown
    _AbsChange > 100,  "#E8A33D",  // amber — notable shift
                       "#0E8A6E"   // teal — within normal range
)
```

**Why this matters:** semantic color isn't decoration. It's the second axis of the visual — the bar length shows magnitude, the color shows whether magnitude crosses a threshold worth attention. Pairing the two compresses two questions ("how big?" and "how worried should I be?") into one glance.

---

## 6. Risk Summary — the data-driven action register

> **Pattern:** a static table populated entirely by measures, generating a four-row signal-finding-action register.

The Movements page's Risk Summary card is the dashboard's most differentiated visual. A small `DATATABLE` defines four risk categories. Three measures — `[Risk Finding]`, `[Risk Action]`, `[Risk Severity Color]` — populate the rows dynamically based on current model state.

**Sketch:**

```dax
Risk Finding =
SWITCH(
    SELECTEDVALUE(RiskCategories[Signal]),
    "Adjustments",
        VAR _Count = [Adjustment Count]
        RETURN _Count & " adjustment events flagged",
    "Net Drift",
        VAR _Net = [Net Inventory Change]
        RETURN "Net change of " & FORMAT(_Net, "+#,##0;-#,##0"),
    "Replenish/Sales Gap",
        VAR _Gap = [Replenishment Qty] - [Sales Issue Qty]
        RETURN "Replenishment " & IF(_Gap > 0, "exceeding", "trailing") & " sales by " & FORMAT(ABS(_Gap), "#,##0"),
    "Slow Movers",
        VAR _Count = [Overstocked SKUs]
        RETURN _Count & " SKUs at >90 days cover"
)
```

**Why this matters:** a hardcoded action register decays the moment data shifts. This one re-reads the model on every refresh and re-narrates itself. It's the difference between a *report* and a *system*.

---

## What this set is meant to show

These six measures are not the most syntactically clever DAX in the model. They were chosen because each one represents a moment in the build where an analytical decision had to be made — and that decision shows up in the code.

- Filter-aware narration encodes *empathy for the reader*.
- Defensive snapshot logic encodes *respect for edge cases*.
- The blank-row guard encodes *paranoia about silent failure*.
- The overstock reframe encodes *analytical judgment over procedural execution*.
- Severity coloring encodes *visual semantics*.
- The Risk Summary encodes *the difference between reporting and a system*.

These are the qualities I'd want a hiring manager to read off the model.

---

> Back to: [`README.md`](../README.md) | Previous: [`03-data-model.md`](03-data-model.md)
