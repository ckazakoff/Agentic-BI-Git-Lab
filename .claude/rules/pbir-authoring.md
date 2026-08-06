# PBIP / PBIR authoring — hard-won rules

Everything here was learned the expensive way while building `lab-report/`. Power BI Desktop
reports a bad project as **"Something went wrong"** with an Activity ID and no actionable message,
so these failures all look identical from the outside. Read this before hand-editing a PBIP.

## Validate first — don't guess from Desktop

```powershell
npx -y @microsoft/powerbi-report-authoring-cli@latest validate lab-report/LabReport.pbip --format text
```

Named, file-and-line diagnostics (`PBIR_PAGE_JSON_MISSING`, `PBIR_SCHEMA_VALIDATION_ERROR`, …) in
seconds. It turns an afternoon of guessing into one command.

The companion CLI drives a running Desktop:

```powershell
npx -y @microsoft/powerbi-desktop-bridge-cli@latest status
npx -y @microsoft/powerbi-desktop-bridge-cli@latest screenshot <pageId> --output out.png
```

A screenshot is the **only** way to confirm a visual actually rendered — the validator can pass on
a report whose visuals never appear.

> **Store-install gotcha:** the bridge's `open` only probes `Program Files\...\PBIDesktop.exe` and
> can't find a Microsoft Store install. Launch it yourself with
> `$env:LOCALAPPDATA\Microsoft\WindowsApps\PBIDesktopStore.exe "<file>.pbip"`; `status` and
> `screenshot` then work fine. Or set `PBI_DESKTOP_PATH` to the WindowsApps `bin\PBIDesktop.exe`.

## Folder names must equal the object id

The most expensive mistake. PBIR resolves a page by matching the **folder name** under
`definition/pages/` to the entry in `pages.json` → `pageOrder` (which equals `name` in `page.json`),
and a visual by matching its folder to `name` in `visual.json`. Both are 20-char hex ids:

```
definition/pages/1a2b3c4d5e6f70819200/page.json
definition/pages/1a2b3c4d5e6f70819200/visuals/9f8e7d6c5b4a39281706/visual.json
```

Name a folder `Lab.Page` or `SalesTable.Visual` and it is **silently skipped** — the project opens,
the model loads, and the page or visual simply isn't there. Older exported reports use the
friendly-name style, which makes copying that layout a convincing wrong turn. `validate` catches
the page case; it was silent on the visual case, which only a screenshot revealed.

## `$schema` URLs — the `.pbip` is the odd one out

Desktop schema-validates every file on open and rejects the whole project on a mismatch. The
`.pbip` shortcut file's schema is **not** under `item/` like everything else:

| File | path after `json-schemas/fabric/` |
|---|---|
| `<name>.pbip` | `pbip/pbipProperties/1.0.0` |
| `<n>.Report/definition.pbir` | `item/report/definitionProperties/2.0.0` |
| `<n>.SemanticModel/definition.pbism` | `item/semanticModel/definitionProperties/1.0.0` |
| `.platform` (both artifacts) | `gitIntegration/platformProperties/2.0.0` |
| `definition/report.json` | `item/report/definition/report/3.0.0` |
| `definition/pages/pages.json` | `item/report/definition/pagesMetadata/1.0.0` |
| `definition/pages/<P>/page.json` | `item/report/definition/page/2.0.0` |
| `.../visuals/<V>/visual.json` | `item/report/definition/visualContainer/2.4.0` |
| `definition/version.json` | `item/report/definition/versionMetadata/1.0.0` |

A local (rather than published) model is `datasetReference.byPath.path = "../<n>.SemanticModel"` in
`definition.pbir`.

## `report.json` requires `themeCollection`

A minimal `report.json` of just `$schema` + `settings` fails: *must have required property
'themeCollection'*. And `baseTheme` in turn requires `reportVersionAtImport`:

```json
"themeCollection": { "baseTheme": {
  "name": "CY24SU10",
  "reportVersionAtImport": { "visual": "1.8.95", "report": "2.0.95", "page": "1.3.95" },
  "type": "SharedResources" } }
```

Referencing a stock base theme this way needs **no** bundled theme file — useful for a public repo.

## A visual's title is container chrome, not data formatting

`visual.visualContainerObjects.title`, **not** `visual.objects.general`. Note the doubled quoting —
string literals carry their own single quotes inside the JSON string:

```json
"visualContainerObjects": { "title": [ { "properties": {
  "show": { "expr": { "Literal": { "Value": "true" } } },
  "text": { "expr": { "Literal": { "Value": "'Sales by Customer'" } } } } } ] }
```

`objects.general` legitimately appears on textboxes and slicers, which is what makes it a tempting
wrong turn.

## MAX_PATH kills *opening* a project, silently

Desktop launches, shows **"Untitled - Power BI Desktop"**, never loads the project, and emits no
error and no Frown snapshot; the bridge returns `bridgeStatus: error`. Indistinguishable from a
corrupt project. A real report's deepest file is ~112 characters on its own, so a repo cloned into
a deep or OneDrive-synced folder blows the 260-character limit as soon as anything is copied a
level deeper. **Measure the path before debugging the PBIR:**

```powershell
(Resolve-Path .).Path.Length    # keep the project root under ~145
```

`C:\dev\` is the safe habit.

## Calculated tables need no credentials and no refresh

`DATATABLE(...)` and `ADDCOLUMNS(CALENDAR(...), ...)` in a `partition X = calculated` give a model
that opens **with data** on any machine — no data source, gateway, credentials or refresh step.
Import-mode M partitions, by contrast, come back `State=3` (NoData) on **every** open of a `.pbip`,
not just the first, because a PBIP carries no data cache.

Two shape details: DATATABLE takes dates as ISO **strings** (`{"2025-01-14", …}` against a
`DATETIME` column), and calculated-table columns are declared with `isNameInferred` +
`sourceColumn: [Name]` (bracketed) — not the plain `sourceColumn: Name` of an M-partition table.
`dataCategory: Time` on the table is enough to mark it as a date table.

Desktop may still show a *"calculated objects need to be manually refreshed"* banner on open; if
the numbers are on screen, it's cosmetic.

## Desktop reads the project on open

It will not pick up file changes while running. After any TMDL or JSON edit on disk, **close and
reopen** the `.pbip`. Expect to be caught by this at least once.
