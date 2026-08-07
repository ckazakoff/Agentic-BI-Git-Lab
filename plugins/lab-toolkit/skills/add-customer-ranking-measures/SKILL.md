---
name: add-customer-ranking-measures
description: Add Customer Rank and Top 5 Customer Sales measures to a Power BI PBIP semantic model using RANKX and TOPN. Use when asked to rank customers, show a top-N leaderboard or "top 5 customers" figure, or when an existing rank measure returns 1 on every row, ranks against the whole fact table, or breaks ties the wrong way.
---

# Customer ranking measures (RANKX / TOPN)

Adds two measures to a PBIP semantic model: a rank per customer, and the sales total of the top
five customers. Follow [semantic-model-conventions](../semantic-model-conventions/SKILL.md) for
everything not covered here.

## Where it goes

`<Model>.SemanticModel/definition/tables/Measure.tmdl` — the dedicated measure table, never the
fact table. TMDL is **tab-indented**; a multi-line expression indents one level past the `measure`
line. Leave `lineageTag` out of new measures.

## The two rules that make ranking correct

1. **Rank over the distinct customer column, not the fact table.** `RANKX(ALL(Sales), ...)`
   iterates every order row, so a customer with three orders competes with themselves and the
   ranks come back wrong. Iterate `ALLSELECTED(Sales[CustomerName])`.
2. **`ALLSELECTED`, not `ALL`.** `ALL` ignores slicers, so a filtered page still ranks against
   every customer in the model. `ALLSELECTED` keeps the outer filter context and removes only the
   row's own customer filter — which is what makes ranks read 1–10 down a table visual.

Ties: RANKX's default `Skip` gives `1, 2, 2, 4` — two customers genuinely tied for 2nd and no
3rd place. That is the intended behaviour; only pass `Dense` (`1, 2, 2, 3`) if asked for it.
`TOPN` returns **all** tied rows at the boundary, so a tie for 5th makes `Top 5 Customer Sales`
cover six customers. That is correct, not a bug — say so rather than "fixing" it.

## The exact TMDL

Append inside `table Measure`, after the existing measures, one blank line between each:

```tmdl
	measure 'Customer Rank' =
			IF(
				NOT ISBLANK([Total Sales]),
				RANKX(ALLSELECTED(Sales[CustomerName]), [Total Sales], , DESC)
			)
		formatString: #,0
		displayFolder: Ranking

	measure 'Top 5 Customer Sales' =
			SUMX(
				TOPN(5, ALLSELECTED(Sales[CustomerName]), [Total Sales], DESC),
				[Total Sales]
			)
		formatString: \$#,0;(\$#,0);\$#,0
		displayFolder: Ranking
```

The `IF(NOT ISBLANK(...))` guard stops customers with no sales in the current filter from being
ranked — without it they all land on the same bottom rank and pad the visual.

`Top 5 Customer Sales` deliberately ignores the row's customer, so it returns the same value on
every row of a customer table — put it in a card, not a column.

## Verify

1. Close and reopen the `.pbip` — Desktop reads the model on open.
2. Put `CustomerName`, `Total Sales` and `Customer Rank` in a table, sorted by rank ascending:
   ranks read 1–10 with no gaps except where a real tie skips one.
3. Run `python scripts/validate_plugins.py` before pushing.