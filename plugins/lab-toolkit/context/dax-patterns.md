# DAX patterns

Shared reference the toolkit's skills point at. Extend it as you find patterns worth reusing —
this file is meant to grow, and it is where the lab has everyone add a row.

## Safe division

Never `a / b`. `DIVIDE` returns blank instead of an error when the denominator is zero or blank,
which happens on any period with no rows.

| Instead of | Write |
|---|---|
| `[Sales] / [Orders]` | `DIVIDE([Sales], [Orders])` |
| `[Sales] / [Orders]` with a fallback | `DIVIDE([Sales], [Orders], 0)` |

## Time intelligence

Requires a Date table marked as one (`dataCategory: Time`), contiguous, related to the fact. All of
these take the date **column** explicitly — don't rely on the marking alone.

| Pattern | DAX |
|---|---|
| Year to date | `TOTALYTD([Total Sales], 'Dates'[Date])` |
| Month to date | `TOTALMTD([Total Sales], 'Dates'[Date])` |
| Same period last year | `CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Dates'[Date]))` |
| Previous month | `CALCULATE([Total Sales], PREVIOUSMONTH('Dates'[Date]))` |
| Rolling 12 months | `CALCULATE([Total Sales], DATESINPERIOD('Dates'[Date], MAX('Dates'[Date]), -12, MONTH))` |
| Year over year % | `DIVIDE([Total Sales] - [Total Sales PY], [Total Sales PY])` |

<!-- Lab: add your row at the bottom of the table above. -->

## Ranking

| Pattern | DAX |
|---|---|
| Rank customers by sales | `RANKX(ALL(Sales[CustomerName]), [Total Sales], , DESC, Dense)` |
| Top N total | `CALCULATE([Total Sales], TOPN(5, ALL(Sales[CustomerName]), [Total Sales], DESC))` |

Wrap a `RANKX` in `IF(HASONEVALUE(...), ...)` so it returns blank on the total row instead of 1.

## Percent of total

| Pattern | DAX |
|---|---|
| Share of all customers | `DIVIDE([Total Sales], CALCULATE([Total Sales], REMOVEFILTERS(Sales[CustomerName])))` |
| Share of visible selection | `DIVIDE([Total Sales], CALCULATE([Total Sales], ALLSELECTED(Sales[CustomerName])))` |

`REMOVEFILTERS` ignores slicers; `ALLSELECTED` respects them. Picking the wrong one is the most
common cause of percentages that don't add to 100%.
