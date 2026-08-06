# Facilitator guide — Agentic Development & Git, 60-minute lab

Audience: experienced Power BI developers, new to git, pull requests, CI/CD, and agentic
development. They aren't new to building things — they're new to *this delivery loop*.

Materials:
- [LAB.md](LAB.md) — the participant handout. Share this link; it's what they follow.
- [lab-report/](lab-report/) — the throwaway PBIP the lab tests against ([details](lab-report/README.md)).
- [cheatsheet.md](cheatsheet.md) — commands and jargon, for during and after.
- [prework.md](prework.md) — send 3–5 days ahead.
- [solutions/validate.yml](solutions/validate.yml) — the CI file for the reveal.

---

## The one idea

Everything in the hour serves a single argument:

> An agent makes *writing* code nearly free. That shifts all the value to **testing**,
> **reviewing**, and **undoing** — and git is the tool for all three. That's why we're teaching
> git the same week we're teaching agentic development.

The Power BI half carries the argument. They write a skill, run it against a real semantic model,
and **reopen Desktop to see whether it actually worked**. That moment — agent output, verified in
the tool they trust — is what makes the git half feel necessary rather than administrative.

If they leave able to state that idea and run the loop once, the lab worked.

---

## Prep (the day before — 30 min)

1. **Open the template in Desktop yourself.** `lab-report/LabReport.pbip` — every table is a
   calculated table, so it needs no credentials and no refresh. Confirm the **Lab** page shows
   181 orders and `Total Sales` = **$4,591,650.58**. Verified on Desktop 2.156.951.0, but check it on *your* build — everything
   else depends on it. Troubleshooting is in [lab-report/README.md](lab-report/README.md); fix
   anything on `main` before the pre-work goes out.
2. **Dry-run the whole lab** on a throwaway branch, including writing one skill and applying it.
   Budget 25 minutes. It's the only way to find the one thing that's different on a real machine.
3. **Grant access.** Every attendee needs the **Developer** role on
   `<ORG>/agentic-dev-lab`. Verify with a test push, not by looking at
   the members list.
4. **Protect `main`.** Settings → Repository → Protected branches: `main`, allowed to merge =
   Maintainers, **allowed to push = No one**. A stray `git push` then can't ruin the lab, and the
   "why can't I just push?" question lands naturally.
5. **Merge this workshop branch to `main` first** so everyone clones a repo that already has
   `scripts/validate_plugins.py`, the gitignored `sandbox/`, and the
   **Time intelligence** section in `dax-patterns.md` (that section is the deliberate
   conflict target — the lab does not work without it).
6. **Do not** put `.github/workflows/validate.yml` on `main` — it's the reveal.
7. Confirm `python scripts/validate_plugins.py` prints `RESULT: PASS` on a fresh clone.
8. Have the [cheatsheet](cheatsheet.md) open and pasteable in chat.

---

## Run of show

| Time | Block | You are doing |
|---|---|---|
| 0:00–0:05 | **Framing** | The one idea, above. Then 60 seconds on what a skill is and why PBIP being text is the thing that makes any of this possible. Resist a longer tour. |
| 0:05–0:07 | **Step 1 — branch** | Everyone on a branch, together, screen shared, before anyone touches Claude. Confirm out loud. |
| 0:07–0:09 | **Step 2A — sandbox** | Copy the template, **launch Desktop now** so it loads while you talk. Make the gitignore point here — it's 20 seconds and it's the repo's core rule. |
| 0:09–0:20 | **Step 2B — Claude writes the skill** | They pick from the menu, prompt, and **read the output**. |
| 0:20–0:30 | **Step 2C — run it, prove it in Desktop** | The centrepiece. See below. |
| 0:30–0:34 | **Step 2D — commit** | `git status` shows the skill but not the sandbox. Land that. |
| 0:34–0:39 | **Step 3 — shared file** | One row each, fast. This is loading the gun for Step 6. |
| 0:39–0:41 | **Step 4 — validate** | Run the script. Sell "shift left" in one sentence. |
| 0:41–0:46 | **Step 5 — push + PR** | First time anything leaves their laptop. Slow down; the PR page is unfamiliar. |
| 0:46–0:54 | **Step 6 — merge + conflict** | Merge in sequence; everyone else resolves in parallel. |
| 0:54–0:58 | **CI reveal** | You drive. |
| 0:58–1:00 | **Wrap** | The takeaway table at the end of LAB.md, plus what to do Monday. |

### Step 2B — the discipline moment (0:09–0:20)

The temptation is to let them marvel at how fast Claude writes the file. Redirect within a minute:
everyone opens the `SKILL.md` and finds *one thing to change*. Say it plainly:

> "Nobody merges what they haven't read. The agent is fast, confident, and occasionally wrong —
> and it's your name on the commit."

### Step 2C — the payoff (0:20–0:30)

This is the block that justifies the whole hour. Three things to police:

1. **They must close and reopen Desktop, then Refresh again.** Desktop reads the model from disk
   only when it opens a project, and a reopened PBIP always comes back with no data. Expect several
   people to conclude "it didn't work" after missing one or the other. Call out both *before* they
   hit it — it's the single most common stumble in the lab.
2. **They must actually build the card or matrix.** Seeing a measure appear in the Data pane is
   not proof it returns the right number. Make them look at a value.
3. **A failure here is a win, not a problem.** If someone's DAX is wrong, Desktop says so — that's
   the fastest, most concrete feedback in the entire lab. Have them tell Claude the error and fix
   *the skill*, not just the model. Say:

   > "This is the loop. The skill isn't done when it's written, it's done when the thing it
   > produces works. That's the difference between using an agent and supervising one."

If someone finishes early, have them re-run their skill on a *fresh* copy of the template — a good
skill works twice. That's a real quality bar and it fills the time productively.

### Step 6 — the conflict (0:46–0:54)

Merge the PRs **one at a time**, on your screen, in order. The first is clean. The second shows
*merge blocked*. Say:

> "Nothing has gone wrong. Two people edited the same lines and git refuses to guess which one to
> throw away. It's asking you to decide."

Everyone else resolves in parallel — they don't wait their turn:

```powershell
git switch main; git pull; git switch lab/<yourname>; git merge main
```

The lab uses `git merge main`, **not `git rebase`**, on purpose: no force-push, no rewritten
history, same conflict markers either way. Mention rebase exists; don't teach it today.

Watch for people who "resolve" by deleting the other person's row. Catch it — that's exactly the
silent loss the conflict prompt exists to prevent.

Drowning? Point at GitHub's **Resolve conflicts** button and move on. Finishing the loop beats
finishing the lesson.

### CI reveal (0:54–0:58)

You drive; they watch. It closes the loop from Step 4.

1. "You ran that validator by hand. What happens when someone forgets?"
2. New branch, and have Claude Code write the pipeline:
   ```
   Write a .github/workflows/validate.yml that runs `python scripts/validate_plugins.py` on every pull request
   targeting main and on every push to main. Use a python:3.12-slim image. Keep it minimal.
   ```
   Reference answer: [solutions/validate.yml](solutions/validate.yml) — compare, don't paste.
3. Commit, push, open the PR, show the **Pipelines** tab.
4. **Be straight about the runner.** There's no GitHub Actions runner on this project, so the pipeline
   won't execute — it'll sit pending or show nothing. Don't hide it; use it:

   > "This is the config. The thing that *runs* it is a runner — a machine that picks up the job.
   > We don't have one wired to this project yet, so this is where CI stops for us today. CI is
   > two halves: the pipeline definition, which lives in the repo and gets reviewed like any other
   > code, and the runner, which is infrastructure someone provisions."

5. Land the point: the file CI runs is the *same file* they ran locally. One definition of
   "correct", run in both places.

---

## Failure modes, and what to do

| Symptom | Cause | Fix |
|---|---|---|
| Desktop opens blank ("Untitled"), no error, project never loads | **Windows 260-char path limit** — their clone is too deep (OneDrive-synced Documents is the usual culprit) | Re-clone to `C:\dev\`. Catch it in pre-work: have them send `(Resolve-Path .).Path.Length` — anything over ~145 will fail once the sandbox copy is made |
| Desktop: model changes not showing | Desktop was left open | Close it fully and reopen the `.pbip`. The most common issue in the lab — pre-empt it |
| Tables open with no rows | Fresh PBIP has no cached data | **Refresh** once in Desktop |
| `.pbip` won't open / opens as text | PBIP preview feature off (older builds) | Options → Preview features → **Power BI Project (.pbip) save option**, restart Desktop |
| Desktop errors on the model after the agent's edit | The agent's DAX or TMDL is wrong | This is the lesson, not a defect — feed the error back to Claude. Worst case, delete the sandbox and re-copy |
| Someone edited `lab-report/` instead of their sandbox | Missed Step 2A | `git restore lab-report/` and re-copy. Good moment to show that git undoes mistakes |
| `git push` → 403 | Not a Developer on the project | Add them, or pair them with a neighbour |
| Push rejected on `main` | They never branched | `git switch -c lab/<name>` — their commits come with them |
| `python` not found | Store python stub or PATH | `py scripts/validate_plugins.py`; if that fails, skip Step 4 for them |
| Claude edits files outside the sandbox | Prompt scope ignored | `git restore <file>` — and note this is *precisely* why we branch |
| Running 10 min late | Normal | Cut Step 3 to "add your row, commit, move on" and shorten the CI reveal to showing the file. **Never cut Step 2C or Step 6** — the Desktop proof and the conflict are the two things they can't get from a doc |

---

## If you get 90 minutes instead of 60

In order of value:

1. **`git log` and `git revert`** (10 min) — history and the undo button. Have them revert their
   own merged commit and watch `main` go back. Nothing builds confidence in agentic work faster
   than proving a bad change is one command from gone.
2. **Review each other's PRs properly** (10 min) — line comments, request changes, push a fixup
   commit, watch the PR update.
3. **A second pass on the skill** (10 min) — apply someone *else's* skill to your sandbox. It
   either works on a model the author never tested, or it doesn't — which is the most honest
   possible lesson about writing instructions for an agent.

---

## After the lab

Send within a day, while it's warm:

- The link to `main` showing everyone's merged commits — a shared artifact they built together.
- [cheatsheet.md](cheatsheet.md).
- One concrete assignment: *"next real gotcha you hit in Power BI or Fabric, add it to
  `.claude/rules/` on a branch and open an PR."* A second rep within a week is what makes it
  stick; a workshop alone won't.
