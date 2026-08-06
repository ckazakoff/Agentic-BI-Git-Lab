# Cheat sheet — git, pull requests, and Claude Code

Keep this open during the lab. Everything here is what you'll actually use in a week of normal work.

## The jargon, in plain terms

| Term | What it actually is |
|---|---|
| **repository (repo)** | A folder whose entire history git tracks. |
| **clone** | Download a copy of the repo, history and all. Done once. |
| **`main`** | The shared branch that is always supposed to work. You don't edit it directly. |
| **branch** | Your own copy of the files to change freely. Cheap, disposable, private until you push. |
| **working tree** | The files as they sit on your disk right now. |
| **staging area (index)** | The pile of changes you've marked to go into the next commit (`git add` puts them there). |
| **commit** | A permanent, named save point. The unit of "one change". |
| **`HEAD`** | Shorthand for "the commit I'm currently sitting on". |
| **remote / `origin`** | The copy on the GitHub server. `origin` is its default nickname. |
| **push / pull** | Send your commits up / bring others' commits down. |
| **pull request (PR)** | GitHub's name for a pull request: "please review my branch and put it on main". |
| **merge conflict** | Two branches changed the same lines. Git won't guess — you choose. |
| **CI/CD pipeline** | Checks that run automatically on your PR (here: the plugin validator). |
| **runner** | The machine that actually executes a pipeline. No runner = no pipeline runs. |

## The eight commands that cover ~90% of the work

```powershell
git status                       # what branch am I on, what changed?  Run this constantly.
git switch -c lab/jsmith         # create a branch and move to it
git switch main                  # move to an existing branch
git diff                         # what changed, line by line (unstaged)
git add <path>                   # stage changes for the next commit  (git add -A = everything)
git commit -m "message"          # save a snapshot of what's staged
git push -u origin HEAD          # send this branch to GitHub (first push; after that just `git push`)
git pull                         # bring down the latest commits for the branch you're on
```

## Recipes

**Start a new piece of work**
```powershell
git switch main
git pull
git switch -c lab/jsmith
```

**Undo — the four kinds**
```powershell
git restore <file>               # throw away uncommitted changes to a file
git restore --staged <file>      # unstage, but keep the edits
git commit --amend               # fix the message or contents of the commit you JUST made (before pushing)
git revert <commit-hash>         # make a new commit that undoes an old one (safe after pushing)
```

**See history**
```powershell
git log --oneline -10            # last 10 commits, one line each
git log --oneline --graph --all  # the branch picture
git show <commit-hash>           # exactly what one commit changed
```

**Resolve a conflict** (what Step 6 walks through)
```powershell
git switch main
git pull
git switch lab/jsmith
git merge main                   # -> CONFLICT
# edit each conflicted file: keep what should survive, delete the <<<<<<< ======= >>>>>>> lines
git add <the-file>
git commit                       # accept the default message
git push
```

**Conflict markers, decoded**
```
<<<<<<< HEAD
your version (the branch you're on)
=======
their version (what you're merging in)
>>>>>>> main
```
Delete all three marker lines. Keep whichever content is correct — often **both**.

**Open a pull request from the terminal** (GitHub push options — skips the web form)
```powershell
git push -o merge_request.create -o merge_request.target=main -o merge_request.remove_source_branch
```

## Before every push

```powershell
python scripts/validate_plugins.py     # RESULT: PASS before you push
```

## Working with Claude Code

```powershell
claude                    # start it in the current folder
```

| In-session | What it does |
|---|---|
| `/plugin` | Manage installed plugins and marketplaces |
| `/mcp` | Check which MCP servers are connected |
| `/clear` | Wipe the conversation and start clean — do this between unrelated tasks |
| `Esc` | Interrupt Claude mid-answer |
| `#` at the start of a message | Save a note to memory / CLAUDE.md |

**Prompting habits that matter in a git repo**

- **Scope it.** "Create only `<path>`. Do not modify anything else." An unscoped agent edits more
  than you expect, and you'll find it in `git status` — but easier to prevent than to unpick.
- **Point at an example.** "Match the format of `<existing file>`" beats describing the format.
- **Commit before a risky ask.** A clean working tree means `git restore .` puts everything back.
- **Read the diff before you commit.** `git status` then `git diff`. Every time. This is the job now.
- **Small commits.** One idea per commit. When something turns out wrong, you revert one commit,
  not a day's work.

## PBIP — why any of this works on Power BI

A `.pbix` is a binary blob: git can store it but can't diff it, review it, or merge it, and an
agent can't edit it. A **PBIP** is the same report saved as plain text files, which is what makes
everything in this lab possible.

```
LabReport.pbip                    <- open this in Desktop
LabReport.SemanticModel/
  definition/model.tmdl               <- model-level settings, `ref table` lines
  definition/relationships.tmdl
  definition/tables/Measure.tmdl      <- MEASURES go here, never on a fact table
  definition/tables/Sales.tmdl        <- columns + the calculated partition (the data)
  definition/tables/Dates.tmdl        <- date table
LabReport.Report/
  definition/report.json              <- theme, report settings
  definition/pages/<pageId>/visuals/<visualId>/visual.json
```

**Folder names must be the object's id.** `pages/<pageId>/` and `visuals/<visualId>/` have to match
the `name` inside the JSON (and the entry in `pages.json` → `pageOrder`). A friendly folder name
like `Lab.Page` is silently ignored — the report opens but the page or visual just isn't there.

- **TMDL** (`.tmdl`) is the model: tables, columns, measures, relationships. **Tab-indented** —
  spaces will break it.
- A measure in TMDL looks like this; `formatString` and `displayFolder` are optional, and Desktop
  fills in `lineageTag` itself if you leave it out:
  ```
  	measure 'Total Sales' = SUM(Sales[Amount])
  		formatString: \$#,0;(\$#,0);\$#,0
  		displayFolder: Core
  ```
- **Desktop reads these files when it opens the project.** After any edit on disk — by you or by
  an agent — you must **close and reopen** the `.pbip`. This catches everyone at least once.
- Enable it for your own work: File → Options and settings → Options → Preview features →
  **Power BI Project (.pbip) save option**, then *Save as* → `.pbip`.

## Where the knowledge lives in this repo

| Path | What goes there |
|---|---|
| `plugins/lab-toolkit/skills/` | Reusable skills — how to do a job |
| `plugins/lab-toolkit/context/` | Reference material skills point at (mappings, examples) |
| `.claude/rules/` | Hard-won CLI gotchas, loaded automatically in this repo |
| `CLAUDE.md` | The repo's conventions — read before contributing |

Rule of thumb: **reusable knowledge goes in the repo; a specific engagement's files never do.**
