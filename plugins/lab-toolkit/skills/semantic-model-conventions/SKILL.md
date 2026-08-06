---
name: semantic-model-conventions
description: Apply the house conventions to a Power BI semantic model in TMDL - where measures live, how they are named and formatted, and which columns get hidden. Use when adding or reviewing measures in a PBIP, when a model has been generated or imported and needs tidying to standard, or when asked to "make this model follow our conventions".
---

# Semantic model conventions (TMDL)

The house rules for a Power BI semantic model saved as a **PBIP**, where the model is TMDL text
on disk. This skill is also the **format example** for skills written during the lab — match its
shape: frontmatter, a short statement of purpose, the exact edit to make, and a worked example.

## Where things go

| Object | Home |
|---|---|
| Measures | The dedicated `Measure` table — **never** on a fact table |
| Columns | The table they belong to; technical keys hidden |
| A new table | Its own file under `definition/tables/<Name>.tmdl`, plus a `ref table <Name>` line in `model.tmdl` |

## Rules

1. **Measures live in `Measure.tmdl`.** Adding one anywhere else scatters them across the Data
   pane and makes them impossible to find.
2. **TMDL is tab-indented.** Spaces will not parse. Match the surrounding indentation exactly.
3. **Every measure gets a `formatString`.** Currency `\$#,0;(\$#,0);\$#,0`, whole numbers `#,0`,
   percentages `0.0%;-0.0%;0.0%`.
4. **Group with `displayFolder`** once a table has more than a handful of measures.
5. **Always `DIVIDE(a, b)`, never `a / b`.** `DIVIDE` returns blank instead of an error when the
   denominator is zero — which happens on any period with no rows.
6. **Hide technical columns** — surrogate keys, sort-by columns, anything a report author should
   never drag onto a canvas: add `isHidden` to the column.
7. **Leave `lineageTag` out of new objects.** Power BI Desktop generates one on first save; a
   hand-written tag is not required and a duplicated one is harmful.

## Worked example

Adding a measure to `Measure.tmdl` — note the tab indentation and the blank line between measures:

```tmdl
	measure 'Avg Order Value' = DIVIDE([Total Sales], [Order Count])
		formatString: \$#,0;(\$#,0);\$#,0
		displayFolder: Order Value
```

Hiding a technical column, in the table's own `.tmdl` file:

```tmdl
	column zKeyBusinessentityidFiscalquarter
		dataType: string
		isHidden
		summarizeBy: none
		isNameInferred
		sourceColumn: [zKeyBusinessentityidFiscalquarter]
```

## Before you finish

- Run `python scripts/validate_plugins.py` — it checks skill frontmatter and repo structure.
- Power BI Desktop reads the model **when it opens the project**. To see a TMDL change, close and
  reopen the `.pbip`; it will not pick up edits while running.
