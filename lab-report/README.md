# LabReport — the workshop's test-bed PBIP

A deliberately small Power BI project used by [the lab](../LAB.md) so that a skill written by
Claude Code can be **proved to work in Power BI Desktop**, not just read on screen.

**Do not edit this folder during the lab.** Copy it to your own sandbox first (Step 2A):

```powershell
Copy-Item -Recurse lab-report sandbox\<yourname>
```

`sandbox/` is gitignored. That's deliberate, and it's this repo's core principle in miniature: the
*skill* is reusable knowledge and belongs in git; your test report is a work artifact and does not.
See [CLAUDE.md](../CLAUDE.md).

## What's in the model

Everything is a **calculated table** — pure DAX, no Power Query, no data source, no credentials, no
gateway, and **no refresh step**. It opens with data on any machine with nothing configured.

| Table | Rows | Contents |
|---|---|---|
| `Sales` | 181 | Orders from Jan 2024 → Dec 2025. `SalesTotal` totals **$4,591,650.58**, 10 customers, 4 salespeople, 3 order types |
| `Dates` | 731 | `Date`, `Year`, `Month` (sorted by `Month Number`), `Month Number`, `Quarter`; marked as a date table |
| `Measure` | 1 | The measure container — measures live here, never on a fact table |

- Relationship: `Sales[OrderDate]` → `Dates[Date]`.
- Two measures to build on: **`Total Sales`** (`SUM(Sales[SalesTotal])`) and **`Order Count`**
  (`COUNTROWS(Sales)`).
- `Sales` carries the columns the lab's skills need: `SalesSubTotal` / `SalesTax` / `SalesFreight`
  for value ratios, `LateShipRating` and `ShipDate` / `DueDate` for shipping performance,
  `CustomerName` for ranking, and deliberately untidy `zKey…` / `*AddressID` columns to hide.

Useful figures to check work against: **Avg Order Value $25,368.24**, **On Time 43.6%**
(79 On Time / 60 Late / 42 At Risk), **Tax 8.00%**, **Freight 2.26% of sales**.

The report has one page, **Lab**, with a table of Sales by Customer. It exists so that opening the
file proves the model actually evaluated.

## Files

```
LabReport.pbip                          <- open THIS in Power BI Desktop
LabReport.SemanticModel/
  definition/model.tmdl                 <- `ref table` lines; add new tables here too
  definition/relationships.tmdl
  definition/tables/Measure.tmdl        <- measures go here
  definition/tables/Sales.tmdl
  definition/tables/Dates.tmdl
LabReport.Report/
  definition.pbir                       <- byPath -> ../LabReport.SemanticModel
  definition/report.json
  definition/pages/<pageId>/visuals/<visualId>/visual.json
```

Verified opening cleanly on **Power BI Desktop 2.156.951.0 (July 2026), Store build** — all three
calculated tables evaluate on load, so the table shows data immediately with no Refresh.

## Opening it

Launch **Power BI Desktop** → **File → Open report → Browse this device** → `LabReport.pbip`.

> Double-clicking in Explorer often doesn't work — `.pbip` frequently has no default app
> association. If Windows asks, choose Power BI Desktop and tick "Always use this app".

## If something goes wrong

1. **Tables appear but are empty** — click **Refresh** once. Calculated tables normally evaluate on
   load, but Desktop occasionally asks.
2. **Model changes not appearing** — Desktop reads these files when it *opens* the project. After
   any edit on disk, **close and reopen** the `.pbip`.
3. **Desktop opens blank ("Untitled") and never loads the project, with no error** — almost always
   the **Windows 260-character path limit**. Clone to a short path such as `C:\dev\`. Check with
   `(Resolve-Path .).Path.Length`.
4. **`.pbip` won't open** — see the association note above; and check Options → Preview features →
   **Power BI Project (.pbip) save option**.
5. Nothing here is precious. Delete your sandbox copy and copy the template again.

## PBIR gotcha worth knowing

Page and visual folder names **must equal the object's id** — `pages/<pageId>/` and
`visuals/<visualId>/`, matching `name` in the JSON and the entry in `pages.json` → `pageOrder`.
Friendly names like `Lab.Page` are silently ignored: the report opens but the page or visual simply
isn't there. Validate with:

```powershell
npx -y @microsoft/powerbi-report-authoring-cli@latest validate lab-report/LabReport.pbip --format text
```
