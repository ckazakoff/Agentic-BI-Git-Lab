# Pre-work — send before the lab

The lab is 60 minutes and every minute is hands-on. Installing tools during the session kills it,
so this has to be done beforehand. Send the note below, then follow up individually with anyone
who hasn't replied 24 hours ahead — chasing three people the day before is much cheaper than
losing fifteen minutes on the day.

**Step 5 is the one that matters most.** It has every attendee open the lab's Power BI project on
their own machine, which validates the template across every laptop in the room *before* you're
standing in front of them. Don't let anyone skip it.

---

**Subject: 15 min of setup before Thursday's agentic dev + git lab**

Hi all,

Thursday we're doing a hands-on hour. You'll write a Claude Code "skill" that applies a house
convention to a Power BI semantic model, run it against a real model, **check in Power BI Desktop
that it actually worked**, and then take it through the full delivery loop — branch, review, merge
request, merge. No slides.

It's fully hands-on, so **please do these five things before we start.** About 15 minutes. Reply
with the output of step 4 and a yes/no on step 5, and I'll sort out anything that misbehaves in
advance.

**1. Install git** — <https://git-scm.com> (or the software centre). Then set your identity, which
is what stamps your name on every commit:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@yourcompany.com"
```

You'll also need **Power BI Desktop** installed (you almost certainly have it) — we use it in the
lab to check the agent's work.

**2. Install Claude Code** and sign in:

```powershell
irm https://claude.ai/install.ps1 | iex
claude          # follow the sign-in prompt, then type /exit
```

The VS Code extension is optional but nice — search "Claude Code" in the Extensions panel.

**3. Clone the repo** — please use a **short path** like `C:\dev`, not a deep or OneDrive-synced
Documents folder. Power BI projects nest files deeply and a long folder path pushes them past
Windows' 260-character limit, after which Desktop refuses to open the project without saying why:

```powershell
mkdir C:\dev -Force; cd C:\dev
git clone https://github.com/ckazakoff/Agentic-BI-Git-Lab.git
cd Agentic-BI-Git-Lab
```

If that fails with a permissions error, tell me — it means I haven't added you to the project yet.

**4. Confirm it all works** and send me the last two lines:

```powershell
git --version
claude --version
python scripts/validate_plugins.py
```

You should see `RESULT: PASS`. If `python` isn't recognised, try `py` instead; if neither works,
let me know and we'll get Python on your machine.

**5. Open the lab's Power BI project once** — this is the important one. It confirms Power BI
Desktop can open the project we'll all be working against:

```powershell
Copy-Item -Recurse lab-report sandbox\test
```

Then open **Power BI Desktop** → **File → Open report → Browse this device** → pick
`sandbox\test\LabReport.pbip`. (Open it from inside Desktop like this rather than
double-clicking — `.pbip` files often have no default app association.)

You should get a report called **LabReport** with one page, **Lab**, showing a table of sales by
customer — **181 orders totalling $4,591,650.58**. It should show data immediately: every table is
a calculated table, so there is no data source and nothing to refresh.

Nothing should ask you for credentials or a data source. If it does, tell me — that's a bug in the
template copy and I want to know before Thursday.

Then close Desktop and delete the test copy: `Remove-Item -Recurse sandbox\test`

Tell me yes/no on this one. If it doesn't open, send me a screenshot of the error — I'd much
rather fix it Tuesday than Thursday.

**No prep needed beyond that.** You don't need to know any git — that's the point of the session.
Bring a laptop you can install and push from, and a DAX pattern you reach for often (we'll use it in the lab).

See you Thursday.

---

## Facilitator notes on the pre-work

- **The `RESULT: PASS` reply is the real check** — it proves the clone, Python, and repo access
  all work together. A "yep, all set" reply proves nothing.
- **Step 5 is your template smoke test across the whole room.** If the PBIP fails to open on
  someone's build of Desktop, you find out days early instead of losing the centrepiece of the
  lab. Troubleshooting is in [lab-report/README.md](lab-report/README.md).
- Attendees who can't get Power BI Desktop working can still do every git step; they'd just be
  taking the skill's effect on trust. Pair them with someone who can open it.
- **Verify project access separately.** Cloning works with read access; the lab needs *push*.
  Confirm each attendee has the **Developer** role in GitHub.
- If someone can't get Python, they can still do the entire lab minus Step 4 (local validation) —
  don't let it block them.
- Anyone still unset at the start: pair them with a neighbour as navigator rather than debugging
  live. They'll get more out of watching the loop than out of watching an installer.
