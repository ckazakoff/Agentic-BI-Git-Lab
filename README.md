# Agentic BI Git Lab

This lab covers the basics and provides a walkthrough of using AI with Git.

A **60-minute hands-on workshop** for Power BI developers who are new to git, pull requests, CI/CD
and agentic development.

Participants use Claude Code to write a *skill*, run it against a real Power BI semantic model,
**prove in Power BI Desktop that it actually worked**, then take the change through the full
delivery loop:

```
branch  ->  change  ->  test  ->  review  ->  validate  ->  push  ->  pull request  ->  merge
```

The argument the whole hour serves: **an agent makes writing code nearly free, which shifts all the
value to testing, reviewing and undoing — and git is the tool for all three.**

## Start here

| You are | Read |
|---|---|
| A participant | [LAB.md](LAB.md) — the handout you follow, start to finish |
| Running the session | [FACILITATOR.md](FACILITATOR.md) — run-of-show, prep checklist, failure modes |
| Getting people ready | [prework.md](prework.md) — send 3–5 days ahead |
| Looking something up | [cheatsheet.md](cheatsheet.md) — git commands, jargon, PBIP anatomy |

## What's in the repo

```
.claude-plugin/marketplace.json   Claude Code plugin marketplace manifest
plugins/lab-toolkit/              the installable plugin - skills land here
  skills/                         one seed skill; participants add their own
  context/dax-patterns.md         shared reference (and the lab's merge-conflict target)
lab-report/                       LabReport.pbip - the Power BI project to test against
scripts/validate_plugins.py       structure + secret checks; runs locally and in CI
solutions/validate.yml            reference GitHub Actions workflow for the CI reveal
sandbox/                          gitignored - each attendee's throwaway copy
```

## Requirements

- **git**, **Python 3.9+**, **Power BI Desktop**, and **Claude Code** (`irm https://claude.ai/install.ps1 | iex`)
- Write access to this repo, so attendees can push a branch and open a pull request
- **Clone to a short path** such as `C:\dev\` — a Power BI project nests files deeply and a long
  folder path exceeds the Windows 260-character limit, after which Desktop silently refuses to open
  it. See [lab-report/README.md](lab-report/README.md).

No cloud account, database, gateway or credentials are needed. The lab's Power BI model is built
entirely from calculated tables, so it opens with data on any machine with nothing configured.

## Check your setup

```powershell
python scripts/validate_plugins.py     # expect: RESULT: PASS
```

Then open `lab-report/LabReport.pbip` in Power BI Desktop — the **Lab** page should show
181 orders totalling **$4,591,650.58**.

## Conventions

See [CLAUDE.md](CLAUDE.md). The short version: **reusable knowledge goes in the repo; a specific
piece of work does not.** Skills are committed; your sandbox copy of the report is not.

## Licence

MIT — see [LICENSE](LICENSE).
