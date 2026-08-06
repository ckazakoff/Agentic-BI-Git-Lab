# Lab: Ship a change to the toolkit with Claude Code + Git

**60 minutes.** By the end you will have branched this repo, written a skill that Claude Code
then uses to change a real Power BI model, **proved it worked in Power BI Desktop**, had your
work checked automatically, opened a pull request, resolved a merge conflict, and merged to
`main`.

You already know Power BI. What's new is the *delivery loop* around the work:

```
branch  ->  change  ->  test  ->  review  ->  validate  ->  push  ->  pull request  ->  merge
```

That loop is the whole point. Agentic development means an AI writes a lot of your work, fast.
Git is what makes that safe: a branch is a sandbox you can throw away, a diff is how you check
the agent's output, and a pull request is where a human signs off before anything reaches `main`.

> Stuck at any step? Say so and keep moving — the facilitator will catch you up. Nothing you do
> on your own branch can break anything for anyone else. That's what a branch is for.

---

## Step 0 — Get the repo (2 min)

If you already cloned it during pre-work, skip to Step 1.

**Clone somewhere with a short path** — `C:\dev\` is ideal:

```powershell
mkdir C:\dev -Force; cd C:\dev
git clone https://github.com/ckazakoff/Agentic-BI-Git-Lab.git
cd Agentic-BI-Git-Lab
```

> **Why the short path matters.** The Power BI project nests files deeply
> (`…\definition\pages\<pageId>\visuals\<visualId>\visual.json` is 112 characters on its own).
> Cloning into a deep folder — a OneDrive-synced `Documents`, say — pushes those past Windows'
> 260-character limit, and **Desktop then fails to open the project with no useful error**.
> `C:\dev` leaves ~90 characters of headroom; a deep Documents path can leave under 40.

Make sure you're starting from the latest `main`:

```powershell
git switch main
git pull
git status          # should say "working tree clean"
```

`git status` is the most useful command in git. Run it constantly — it always tells you what
branch you're on and what has changed.

---

## Step 1 — Make your branch (2 min)

Never work directly on `main`. `main` is the shared, always-working copy. You work on a *branch*:
your own copy of the repo where you can experiment freely.

```powershell
git switch -c lab/<yourname>
git branch --show-current      # -> lab/jsmith
```

Nothing has been sent anywhere. This branch exists only on your laptop.

---

## Step 2A — Set up your Power BI sandbox (3 min)

This repo ships a copy of the lab's Power BI project at
[lab-report/](lab-report/) — a small Power BI project that exists purely so you can *test* what the
agent writes. Copy it to your own sandbox:

```powershell
Copy-Item -Recurse lab-report sandbox\<yourname>
```

Now open it: launch **Power BI Desktop**, then **File → Open report → Browse this device** and
pick `sandbox\<yourname>\LabReport.pbip`.

> Double-clicking the file in Explorer often *doesn't* work — `.pbip` frequently has no default
> app association. If Windows asks "How do you want to open this file?", choose Power BI Desktop
> and tick "Always use this app".

Desktop takes a minute — **start it now** and read ahead while it opens.

It opens on the **Lab** page showing Sales by Customer. You should see **181 orders** totalling
**$4,591,650.58** (Jan 2024 → Dec 2025) straight away — every table is a calculated table, so there
is no data source, no credentials and nothing to set up.

> Desktop may still show a *"calculated objects need to be manually refreshed"* banner. If the
> numbers are showing, that's cosmetic — dismiss it and carry on.

Three things worth knowing about that folder:

- It's a **PBIP** — a Power BI project saved as plain text files instead of one binary `.pbix`.
  The model is TMDL, the report is JSON. That's what makes it reviewable in git *and* editable by
  an agent. This is the single most important reason your team is moving to PBIP.
- The whole model is **calculated tables** — pure DAX, no data source. That's what makes it open
  with data anywhere, on any machine, with nothing configured. Details in
  [lab-report/README.md](lab-report/README.md).
- `sandbox/` is **gitignored**. Your test report is a work artifact, not reusable
  knowledge, so it never gets committed. The skill you're about to write *is* reusable, so it does.
  That distinction is this repo's core rule.

---

## Step 2B — Have Claude Code write the skill (11 min)

A **skill** is a markdown file that teaches Claude Code how to do a specific job to *our* standard
— it's the unit of reusable knowledge in this repo. You're going to write one that applies a house
convention to the lab template's semantic model.

**Pick a skill nobody else has taken** (call it out so we don't duplicate). Every one of these
edits TMDL only, adds to the model's existing `Measure` table, and is visible in Desktop:

| # | Skill folder name | What it does | How you'll prove it worked |
|---|---|---|---|
| 1 | `add-order-value-measures` | Adds `Avg Order Value`, `Freight % of Sales` and `Tax Rate %` from `SalesSubTotal` / `SalesTax` / `SalesFreight`, using `DIVIDE` (never `/`) | Card shows an average order value near **$25.4K**; no error on months with no orders |
| 2 | `add-shipping-performance-measures` | Adds `On Time %`, `Late Order Count`, `Avg Days to Ship` from `LateShipRating` / `ShipDate` | Card shows `On Time %` = **43.6%** and `Late Order Count` = **60** across all orders |
| 3 | `apply-measure-format-strings` | Gives every measure in `Measure` a house `formatString` and `displayFolder` | `Total Sales` renders as `$4,591,651`; measures group into folders in the Data pane |
| 4 | `add-customer-ranking-measures` | Adds `Customer Rank` and `Top 5 Customer Sales` using `RANKX` / `TOPN` | Table by `CustomerName` ranks 1–10 with no ties broken wrongly |
| 5 | `standardize-column-metadata` | Hides technical columns (`zKey…`, the `*AddressID` keys) and sets `summarizeBy: none` on non-additive numerics | Those columns disappear from the Data pane; IDs stop auto-summing |
| 6 | `add-measure-descriptions` | Adds a `description` to every measure, per the repo's conventions | Hover a measure in the Data pane — the description shows in the tooltip |

Anything you add lands in the model's existing `Measure` table — measures never go on a fact
table. That convention, and the rest, are in
[plugins/lab-toolkit/skills/semantic-model-conventions/SKILL.md](plugins/lab-toolkit/skills/semantic-model-conventions/SKILL.md).

Launch Claude Code in the repo folder:

```powershell
claude
```

And give it this prompt, filling in your choice:

```
Create a new skill at plugins/lab-toolkit/skills/<skill-folder>/SKILL.md.

The skill's job: <what it does, from the table above>

Before writing, read CLAUDE.md for the repo conventions, and read
plugins/lab-toolkit/skills/semantic-model-conventions/SKILL.md as a format example.
Look at lab-report/LabReport.SemanticModel/definition/tables/ to see the TMDL shape
the skill will be editing.

Requirements:
- YAML frontmatter with `name` (matching the folder name) and a `description` that says
  WHEN to use the skill, not just what it does.
- Give the exact TMDL to write and where it goes, with a worked example.
- Client-agnostic: no client names, server names, or project ids.
- Under about 60 lines.
- Create only that one file. Do not modify anything else.
```

**Then read what it wrote.** Open the `SKILL.md`. Is the TMDL right? Would *you* hand this to a
colleague? Ask Claude to revise anything vague — that back-and-forth is the actual work now.

---

## Step 2C — Run the skill and prove it in Desktop (10 min)

Your skill isn't installed as a plugin, so Claude won't pick it up automatically. Point at it
directly — a skill is just a file of instructions:

```
Follow the instructions in plugins/lab-toolkit/skills/<skill-folder>/SKILL.md
and apply them to the model at sandbox/<yourname>/LabReport.SemanticModel.

Change only files under sandbox/<yourname>/.
```

Now check the work — in this order:

1. **Read the diff.** `git status` shows the sandbox as untracked (it's gitignored — that's
   expected). Open the changed `.tmdl` file and read the DAX. Does it look right?
2. **Close Power BI Desktop and reopen** `sandbox\<yourname>\LabReport.pbip`. Desktop reads the
   model from disk only when it *opens* a project — it will not pick up file changes while running.
3. **Prove it.** Use the "how you'll prove it worked" column from the table above. Build the card or matrix yourself —
   this is the part you're already expert at.

**If it didn't work, that's the interesting case.** Tell Claude what Desktop said and have it fix
the skill *and* re-apply. That loop — write, run, observe, correct — is agentic development. The
skill is only finished when the thing it produces actually works.

> Your sandbox is disposable. If the model won't open at all, delete the folder, copy the
> template again, and re-run. Nothing is lost.

---

## Step 2D — Commit the skill (4 min)

```powershell
git status
```

Note what git shows: your `SKILL.md` is untracked, and your sandbox is **not listed at all**
because `.gitignore` excludes it. The reusable knowledge is going in; the test artifact isn't.

```powershell
git add plugins/lab-toolkit/skills/<skill-folder>/
git commit -m "Add <skill-folder> skill"
```

- `git add` = "include this in my next commit" (the *staging area*).
- `git commit` = "save a permanent snapshot of what's staged, with a message."

A commit is a save point. You can always come back to one. Commit often.

---

## Step 3 — Extend a shared reference file (5 min)

Open [plugins/lab-toolkit/context/dax-patterns.md](plugins/lab-toolkit/context/dax-patterns.md)
and find the **Time intelligence** section.

**Add one row to the bottom of that table** — a time-intelligence pattern you've actually used, and the DAX for it. One line, your own words.

```powershell
git diff
```

`git diff` shows exactly what changed: `-` removed, `+` added. Get used to reading it — it's how
you review both your own work and an agent's.

```powershell
git add plugins/lab-toolkit/context/dax-patterns.md
git commit -m "Add time intelligence pattern to DAX patterns"
```

Two commits on your branch now. Everyone in the room just edited the *same file* — hold that
thought until Step 6.

---

## Step 4 — Validate before you push (2 min)

Run the repo's own checks:

```powershell
python scripts/validate_plugins.py
```

You want `RESULT: PASS`. If it fails it names the file and the problem — fix, commit, run again.
(It checks exactly the things you might have got wrong: frontmatter present, skill `name` matching
its folder, no committed secrets.)

This same script runs automatically on your pull request later. Running it locally first is
called **shifting left**: catch it in 5 seconds on your laptop instead of 5 minutes into a
pipeline. Make it a reflex before every push.

---

## Step 5 — Push and open a pull request (5 min)

Everything so far is local. Push your branch to the server:

```powershell
git push -u origin HEAD
```

GitHub prints a URL to create the pull request. Click it (or go to the repo in GitHub →
**Pull requests** → **New pull request**).

- **Title:** `Lab: add <skill-folder> skill and DAX map row`
- **Description:** one line on what you added, and one line on how you tested it in Desktop.
- **Target branch:** `main`
- Tick **Delete source branch when pull request is accepted**.

A **pull request** (GitHub's name for a pull request) is a proposal: *"here are my commits,
please review them and put them on main."* It's where review happens, where automated checks
report, and where the conversation lives. It's the gate that keeps `main` trustworthy.

Open the **Changes** tab and read your own diff once more. Then swap with the person next to you
and leave one comment on each other's PR.

---

## Step 6 — Merge, and hit a conflict (10 min)

We merge one at a time. The **first** PR merges cleanly. Everyone after that gets:

> **Merge blocked:** merge conflicts must be resolved.

That's expected — it's why we all edited the same file. Two people changed the same lines, and git
will not guess which one wins. A conflict isn't a failure; it's git refusing to silently lose
someone's work.

Bring the updated `main` into your branch and choose the outcome:

```powershell
git switch main
git pull                        # get the version that just merged
git switch lab/<yourname>
git merge main                  # -> CONFLICT in dax-patterns.md
```

Open the conflicted file. You'll see markers:

```
<<<<<<< HEAD
| your row                    | your DAX |
=======
| their row                   | their DAX |
>>>>>>> main
```

`HEAD` is your version; below `=======` is what's already on `main`. Here we want **both rows** —
delete the three marker lines and keep both. Then:

```powershell
git add plugins/lab-toolkit/context/dax-patterns.md
git commit                      # accept the default merge message
python scripts/validate_plugins.py
git push
```

Refresh your PR — the conflict banner is gone. Merge it.

> **Alternative:** GitHub's PR page has a **Resolve conflicts** button that does this in the
> browser. Fine to use — but do it once in the terminal first so you know what the button does.

---

## Step 7 — Clean up (2 min)

```powershell
git switch main
git pull                        # your change is now on main
git branch -d lab/<yourname>    # delete the local branch; it did its job
```

Look at the measure map — everyone's rows are there, and every skill in the room is on `main`.
That's the loop, completed.

Your sandbox stays on your machine, untracked, exactly as it should.

---

## What you just learned

| You did | The concept | Why it matters for agentic work |
|---|---|---|
| `git switch -c` | Branch | A disposable sandbox. The agent can't hurt anything from inside one. |
| Wrote a skill, then ran it | Skills as code | Agent instructions are files: reviewed, versioned, and improved like any other code. |
| Reopened Desktop to check | Testing the output | "It generated something" is not "it worked". PBIP makes the model text an agent can edit and a human can verify. |
| `git status` / `git diff` | Working tree, diff | How you review what the agent wrote before you put your name on it. |
| `.gitignore` on the sandbox | Artifacts vs knowledge | Reusable rules go in the repo; a specific piece of work doesn't. |
| `python scripts/validate_plugins.py` | Local checks | Catch it in seconds, not minutes. |
| `git push` + PR | Remote, pull request | The human review gate. Nothing reaches `main` unreviewed. |
| `git merge` + resolve | Conflict | Git protects both people's work instead of picking a winner. |

**The one-sentence version:** an agent makes changing things cheap, which makes *reviewing,
testing, and undoing* the valuable skills — and that's exactly what git plus a text-based PBIP
gives you.

Command reference and jargon glossary: [cheatsheet.md](cheatsheet.md).
