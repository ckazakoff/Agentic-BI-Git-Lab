# Agentic Development Lab

A self-contained workshop repo: a **Claude Code plugin marketplace** holding a small Power BI
toolkit, plus a throwaway Power BI project to test changes against. Participants extend the
toolkit during the lab and take the change through branch → review → pull request → merge.

## Layout

| Path | What it is | Committed? |
|---|---|---|
| `.claude-plugin/marketplace.json` | Marketplace manifest | ✅ |
| `plugins/lab-toolkit/` | The installable plugin — this is where **skills** go | ✅ |
| `lab-report/` | `LabReport.pbip` — the test bed the skills are run against | ✅ |
| `scripts/validate_plugins.py` | Structure + secret checks; runs locally and in CI | ✅ |
| `sandbox/` | Each attendee's throwaway copy of `lab-report/` | ❌ gitignored |

## The core rule

**Reusable knowledge goes in the repo; a specific piece of work does not.**

A skill is reusable — it belongs in `plugins/lab-toolkit/skills/`. Your sandbox copy of the report,
the measures you added while testing, the screenshots you took: those are work artifacts and stay
out of git. That is why `sandbox/` is gitignored, and it is the distinction to apply whenever you
are unsure where something belongs.

## Conventions

- Skills are `plugins/lab-toolkit/skills/<name>/SKILL.md` with YAML frontmatter. The `name` in the
  frontmatter **must match the folder name** — the validator enforces it.
- A skill's `description` should say **when to use it**, not just what it does. It is the only
  thing Claude sees when deciding whether the skill applies.
- Keep everything **client-agnostic**: no client names, server hostnames, project ids or
  credentials. The validator scans for committed tokens; it cannot catch a client name, so that
  one is on you.
- Run `python scripts/validate_plugins.py` before every push. The same script runs in CI.

## Editing the Power BI model

`lab-report/` is a **PBIP** — the model is TMDL text, the report is JSON, both diffable in git.

- Measures live in `LabReport.SemanticModel/definition/tables/Measure.tmdl`.
- TMDL is **tab-indented**.
- Page and visual folder names **must equal the object's id** (`pages/<pageId>/`,
  `visuals/<visualId>/`) and match `name` in the JSON. A friendly folder name is silently ignored.
- Desktop reads the project **on open** — close and reopen to see a change.

Full conventions: [plugins/lab-toolkit/skills/semantic-model-conventions/SKILL.md](plugins/lab-toolkit/skills/semantic-model-conventions/SKILL.md).

Hard-won PBIP/PBIR gotchas — schema URLs, why a folder name must be the object id, the Windows
path limit, the validator and Desktop-bridge CLIs — are in
[.claude/rules/pbir-authoring.md](.claude/rules/pbir-authoring.md), which Claude Code loads
automatically when run from this repo. Read it before hand-editing anything under `lab-report/`.
