# The mario Method — Kickoff Gate

*Platform-neutral. This file is the single source of the method; every binding in `agents/`,
`skills/`, and `AGENTS.md` points here rather than restating it.*

Greenfield work fails three ways: building the wrong product, building the right product ugly, and
building something beautiful that nobody can operate. The first two come from writing code before
the target is defined. The third comes from never opening the thing.

Six phases. **No scaffolding, no dependencies, no components until Phase 3 is signed off.**

Design is not handled here — `/impeccable` owns that end to end. This method owns *intent*,
*scope*, the *gate*, and the *first run*.

---

## Running the gate

These hold for every phase, without being asked:

- **Create nothing before Phase 3 approval.** No directory, no `package.json`, no `git init`, no
  "quick scaffold to hold things." If you are about to write, stop and say so instead. This is not
  waivable by `--auto`, by urgency, or by the user seeming impatient.
- **Announce each phase as you enter it**, and announce every agent handoff (`@architect`,
  `@implementer`, …) as it happens, so the chain is visible while it runs.
- **This is a human-in-the-loop workflow. Unattended mode is not available.** There is no `--auto`
  for `start-project`. At every checkpoint below, if no human answers, **stop and wait** — do not
  infer the answer, do not proceed on the most likely reading, do not "keep momentum." A run that
  finishes overnight with nobody awake is the failure this method exists to prevent, not a feature.
- **Ask in batched rounds, never one question at a time and never a form.** At most four questions
  per round, at most three rounds per checkpoint. Use the harness's structured question UI when it
  has one. Extract what the user already told you first and reflect it back for confirmation —
  re-asking what they just said is what makes a gate feel like paperwork.
- **Never skip Phase 2, and never run only part of it.** `/impeccable init` is the first step of
  the design arc, not the whole of it.
- **Never call it done on a passing review.** Craft reviews measure whether a surface is good.
  Only Phase 5 measures whether a person can use it, and it is the one that has been skipped.
- **Do not reproduce copyrighted material.** Reference the structure and pacing of existing
  products; write original content.

### The four checkpoints

Each one stops and waits for a human. They are the spine of the method; everything between them is
work you do on your own.

| # | Where | The user decides |
|---|---|---|
| 1 | Phase 1 | Where the roadmap comes from, and the NOT list |
| 2 | Phase 2 | Which visual direction is locked |
| 3 | Phase 3 | Go / no-go |
| 4 | Phase 5 | Whether the running build is usable |

---

## Phase 1 — Roadmap & Intent

Write nothing yet.

### Checkpoint 1a — where does the roadmap come from?

**Ask this first, before anything else.** Do not assume, and do not start interviewing until it is
answered:

> *"Do you have a roadmap already — written here, in Claude Desktop, or anywhere else — or should
> we build one together now?"*

| Answer | What you do |
|---|---|
| **They have one** | They paste it or name the file. Go to *reconciliation* below. |
| **Build it here** | Run the interview, then **write the roadmap yourself** and put it back to them for correction before it counts. |
| **Just an idea** | Same as *build it here*, starting colder. Expect more rounds. |

A roadmap written elsewhere is often the better artifact — a longer conversation in a bigger
context window usually produces a sharper one than a gate interview will. Take it gladly. It is
still **input, not approval**, and it does not replace a single question below.

### Reconciliation — what to do with a roadmap you were handed

Do not accept it and move on; that is what a one-shot looks like. Read it and split it into three
lists, then show the user all three:

1. **What it answers** — reflected back in one line each, for confirmation.
2. **What it leaves open** — the gaps. These become your question rounds.
3. **What contradicts the NOT list, or contradicts itself.** Say so plainly. A roadmap that names a
   feature the user later refuses is a conflict to settle now, not a surprise to hit at Phase 4.

### The four things you need

Whichever path you came in on:

1. **What is it?** One sentence a stranger would understand.
2. **Who opens it, and what do they do in the first 30 seconds?**
3. **What does it explicitly NOT do?** ← the scope boundary. Force a real answer.
4. **Success looks like…?** A screenshot, signups, a demo?

Ask only for what the roadmap did not already answer. **Q3 is almost never in a roadmap** — people
describe what they want, not what they are refusing. Expect to ask it, and expect the first answer
to be vague. Push once with a concrete wrong-direction guess: *"So it is not just a feed of your
GitHub repos?"*

Record the **NOT list** verbatim. Every later scope question is settled against it.

Capture the **real usage scenario** with it — where the user is, on what device, at what hour, in
what state of mind. Phase 5 tests against that scenario, so a vague answer here produces a build
verified in conditions nobody will ever be in.

**Checkpoint 1b:** put the reconciled roadmap, the NOT list, and the usage scenario back to the
user as one block and get confirmation. This is the last cheap moment to be wrong. The agreed
roadmap is written to `docs/ROADMAP.md` at Phase 4, where `/work plan` can pick it up.

---

## Phase 2 — Design

`/impeccable` owns design end to end. Hand the project over and let it run its **whole arc**. Do
not stop after `init`, and do not cherry-pick commands.

1. **`/impeccable init`** — writes `PRODUCT.md`: users, purpose, positioning, constraints, stack.
   By design it does **not** invent a visual world and does not write `DESIGN.md`.
2. **The direction round** — ask Impeccable, in plain words, to design the surface ("design the
   first screen of <product>"). That is what routes into its `new-work` flow: it rolls an external
   seed, deals candidate directions plus outside challengers, and serves a **decision page on
   localhost** — one card per direction with thesis, palette, materials, first viewport, honest
   risk, and a generated comp. Open the URL for the user.

   **Checkpoint 2 — the user locks a card. You do not pick for them.** They may re-roll, or steer
   *safer* / *bolder*. Record the seed; it reproduces the entire round. If nobody answers, the
   phase stops here; it does not proceed on your favorite.
3. **Whatever `init` recommends next**, and the rest of the arc through the build — `audit`,
   `critique`, `polish`, `onboard` for first-run and empty states.

Feed Phase 1's answers in, especially the NOT list — it becomes Impeccable's anti-references. If
the user supplies reference sites they admire, pass them through; `init` turns references into
tokens far better than prose does.

Skipping the roll is how every project in a category ships the same design. Do not substitute your
own taste, and do not skip because the project is "internal" or "just a tool".

Do not run workforces' `/brand-context` or `@design-pilot`; both are superseded and would produce a
competing brand file.

> **Without Impeccable installed** (Codex, Grok, or a bare harness): the phase still runs, and its
> requirement is unchanged — the user locks a visual direction, chosen from **real referenced
> products**, before any component is written. Present at least three genuinely different
> directions, each named, with its palette, type, first-viewport composition, and honest risk.
> Never one option, never your favorite, never a direction assembled from imagination. Record what
> was chosen and why in `DESIGN.md`.

---

## Phase 3 — Approval Gate

Present a compact summary:

- What it is, who it is for, and **what it will not do**.
- The **direction the user locked**, named, with its seed.
- The stack, and the **absolute path** the project will be created at.
- **How it will run locally** — the dev command and the port.

The deploy target is **not** decided here. Nothing has been built, so nothing constrains the choice
yet, and picking a host before there is a running app narrows the design for no reason. It is
Phase 6.

**Checkpoint 3 — ask for explicit go/no-go.**

**Code begins only after the user says go.** This gate cannot be waived — not by `--auto`, not by
"just start", not by a pasted roadmap.

---

## Phase 4 — Project Setup

Runs once, immediately after approval, before any feature work. Do not ask permission for these
steps individually — approval at Phase 3 covers them. Report the results as one block at the end.

1. **Establish the working directory**, then scaffold the agreed stack inside it. Everything the
   project owns lives under this one root — never scatter files into a parent, a home directory,
   or whatever the shell happened to be sitting in.

   Resolve it in this order:
   - The path the user named. Use it.
   - The current directory, **only if** it is empty or already this project's root. A directory
     holding unrelated work is never the answer.
   - Otherwise **create one named after the project** — kebab-case, derived from the product name
     (`Sleep Stories` → `sleep-stories/`), as a sibling of the user's other projects rather than
     nested inside an unrelated repo.

   Confirm the absolute path at Phase 3 and state it again before the first write. Never create a
   project root inside another project's working tree, and never scaffold into a directory that
   already contains a `.git` you did not just create.
2. **`.gitignore`** for the stack, plus `.env` (never committed) and a committed `.env.example`
   listing every key with placeholder values. Secrets live in `.env` only — never hardcoded,
   never committed.
3. **`docs/ROADMAP.md`** — the roadmap agreed at Checkpoint 1b, verbatim, with the NOT list and the
   usage scenario at the top, then a **Slices** section: each slice's behavior, its one-line
   **Verify by**, and its status. This is what `/work plan` reads later; a roadmap that only exists
   in the transcript is a roadmap the next session cannot use.
4. **The record files**, so the project outlives any single session:
   - `docs/DECISIONS.md` — append-only. `Chose / Over / Because / Revisit if`. When a decision is
     reversed, add an entry superseding the old one; never delete history.
   - `docs/PUNCHLIST.md` — a table of things found but not fixed. Starts empty.
   - `docs/HANDOFF.md` — state, done, in flight, blocked, start-here-next-time. Written at logoff.
5. **`README.md`** — what it is and **how to run it locally**. Written for someone returning in six
   months with no memory of it. Deployment is added in Phase 6, once there is a target.
6. **`CLAUDE.md`** — project-specific instructions: what this project is, its NOT list, its stack
   and run command. Project facts only — the method itself is not copied here, it is reached
   through the bindings in step 11.
7. **`git init`**, then a first commit containing the scaffold only.
8. **Create the remote** — `gh repo create <name> --private --source=. --remote=origin --push`.
   **Private unless the user explicitly asked for public.**
9. **Obsidian** — create `<Project Name>/` in the vault root
   (`/mnt/c/Users/jobid/OneDrive/Documents/X posts/`) with an index note holding the one-liner,
   the NOT list, the locked direction and seed, the repo URL, the local path, and the run command.
   > The vault is under OneDrive. Never run recursive scans (`find`, `grep -r`, `rg`, `ls -R`,
   > `du`) against that path from WSL — it hydrates cloud placeholders and fills the C: drive.
   > Use `powershell.exe -NoProfile -Command "Get-ChildItem ..."` for discovery. Reading and
   > writing individual known files is fine.
10. **Offer to open it.** Ask which editor unless the user has a configured preference — check
   their global instructions first and just use it if one is set. Do not open anything without
   asking or a standing preference; a window stealing focus mid-session is worse than a question.

   | Editor | Command |
   |---|---|
   | VS Code | `code <path>` |
   | Vim / Neovim | `vim <path>` / `nvim <path>` |
   | Other GUI editor | its own CLI |

   On WSL with a Windows-side editor, the folder must open **as a remote WSL workspace**, not via
   a `\\wsl.localhost\...` path — otherwise tooling, terminals, and file watching all run on the
   wrong side. Some editors need an explicit remote flag for this. If the user's global
   instructions record the exact command, use it verbatim.

11. **Install Workforces.** Every project gets it — this is not a question to ask:

    ```bash
    bash ~/antigravity/workforces/skills/workforce-management/scripts/setup.sh ./ \
      --type project --editor antigravity --non-interactive
    ```

    It writes `.agents/` (toolkit) and `workforces/` (workstate, goals, team-sync), which is what
    makes `/work`, `/work plan`, and `/work sync` function. Without it those commands find nothing.

    > **Then neutralize its design layer.** The install ships `@design-pilot`, `@design-reviewer`,
    > and `/brand-context`, all superseded by Impeccable. Delete them from the project's `.agents/`
    > so nothing competes with `DESIGN.md`. Point `/work` at `docs/ROADMAP.md` as its source.

12. **Portable bindings.** So the method survives whatever tool opens this repo next:
    - A gitignored `.mario` symlink at the project root pointing at the mario checkout. A symlink,
      never a copy — a copy stops hearing about edits the day it is made.
    - `AGENTS.md` (three lines, committed): what the project is, and *"This project follows the
      mario method. Read `.mario/METHOD.md` and the role definitions in `.mario/roles/`."*
      Codex, Cursor, and Grok all read a root instruction file; this is the one they get.
    - **`GEMINI.md`**, same three lines. Antigravity detects its workspace by `.gemini/`,
      `GEMINI.md`, or `.agents/` — it does not look for `AGENTS.md`, so without this the project
      opens in Antigravity with no bindings loaded.
    - Add `.mario` to `.gitignore`.
13. **Report** the repo URL, local path, and vault path together.

Then build: `@architect` plans, `@implementer` executes, `/impeccable` designs, `@code-reviewer`
reads. Nothing ships to the user until Phase 5.

---

## Phase 5 — First Run

**The app runs on localhost and someone looks at it before anyone calls it done.**

This phase exists because it is the one that was missing. A build can pass `@architect`,
`@implementer`, `@code-reviewer`, eleven `impeccable audit` runs, `critique`, `shape`, and
`document` — and still open on a screen with an invisible input and no buttons. Every one of those
gates asks whether the output is distinctive, committed, contrast-correct, and free of AI clichés.
**Not one of them asks whether a person could use it.**

1. **Start it.** `npm run dev` or the stack's equivalent. Report the URL. Leave it running.
2. **View it at the size it will actually be used.** Phone viewport for anything mobile-first — not
   a desktop window that happens to be narrow.
3. **Answer all five in writing, against the running build:**
   - What does a first-time user tap or type **first**? Is it visible without being told?
   - Is everything interactive *recognizable* as interactive? Affordance, not just meaning — a
     cliché removed for taste reasons that took the only affordance with it is a defect.
   - Does the primary path complete **end to end** with real input?
   - Does it hold up **in the Phase 1 scenario** — the right hour, device, and state of mind? A
     bedtime app verified at 9am is not verified.
   - **Is the core promise implemented, or stubbed?** Name every stub out loud, in the report, not
     in a code comment. A product whose entire idea is a stub is not a build.
4. **Show the user** screenshots of the real running build. Never mockups, never comps.

**Checkpoint 4 — the verdict is the user's, not yours.** Put the five answers and the screenshots
in front of them and ask directly whether this is usable. Your own "yes" does not close this phase;
four agent reviews and eleven audits already said yes to a screen with no buttons.

Any "no" is a **blocker**, not a note. Fix it and re-run this phase before the reveal.

Then publish the **build report** as an Artifact: the flow state by state with real captures, what
the reviews caught, what is stubbed, and what is left. Hand over the link.

---

## Phase 6 — Deploy Target

Only now, with something running and its real dependencies known.

| Target | Runtime | Choose when |
|---|---|---|
| **Vercel** | Node + Edge, serverless | Frontend-led, SSR/SPA, small API routes. Default for most web work |
| **Cloudflare** | V8 isolates, edge only | Global reach, cost at scale, fastest cold start. **Not full Node** — verify every dependency runs on workerd |
| **Railway** | Containers, persistent | Long-running processes, websockets, cron, background jobs, a database you control |
| **Static host** | None | No server logic at all |

Check the disqualifiers against what the code now actually does: a persistent connection, a job
that outlives a request, a scheduled task, or a dependency needing native Node APIs. Any of those
means Railway (or another container host), not Vercel or Cloudflare.

Name the storage layer too — it is part of the target.

AWS and GCP are not set up for this workflow. If one is required, say so rather than improvising.

Add the deploy section to `README.md` once the target is chosen.

---

## The build loop

Between Phase 4 and Phase 5, work runs **one slice at a time**.

A **slice** is one behavior a human could verify by running the thing. If you cannot state the
verification step in a sentence, the slice is too big — split it. A slice with no verification step
is not a slice.

```
@architect          the slice: files, signatures, edge cases, VERIFY BY
@implementer        build that slice only
/impeccable audit   a11y, contrast, responsive — before the user sees it, not after
/impeccable critique hierarchy, clarity, resonance
@code-reviewer      reads the diff cold, runs the verification itself
@scribe             DECISIONS.md if a real decision was made
   ↑ repeat per slice
Phase 5             run it, use it, screenshot it   ← blocks the reveal
```

### The five rules

1. **Nobody builds without a plan.** A slice with no written definition of done cannot be verified,
   reviewed, or handed off. If you are about to type "just make it work," you skipped the architect
   and will pay for it in rework.
2. **One slice at a time.** Batching three slices before a review means a bug in the first
   contaminates the other two.
3. **The one who builds does not judge.** The implementer shares every assumption that produced the
   bug. The reviewer reads the diff cold and runs the verification itself — on a different model
   where the harness allows it. This is the highest-leverage rule here.
4. **Reading is delegated; writing is not.** Heavy reconnaissance — tracing call sites, evaluating a
   library, touring an unfamiliar codebase — goes to a disposable-context agent. Never burn the
   orchestrating thread's window on a directory tour.
5. **The record outlives the session.** Context does not persist; written state does. Decisions go
   in `docs/DECISIONS.md`, deferred work in `docs/PUNCHLIST.md`, and the state dump in
   `docs/HANDOFF.md` before logging off. A session that ends without a handoff has to be
   reconstructed, and reconstruction is where wrong assumptions creep back in.

### Found something broken outside the current slice?

**Log it to `docs/PUNCHLIST.md`. Do not fix it.** Fixing it means the diff under review is no
longer the slice that was planned, and the reviewer now has two changes tangled together. The
punchlist is what makes "not now" a decision instead of an oversight.

### What "it works" has to mean

Every claim of success **names the command that was run and what it printed.** "It should work,"
"the build passes," and "verified" with nothing attached are not results. This is the cheapest
possible defense against an agent reporting green on something it never executed.

Never ship an empty or placeholder state — `/impeccable onboard` handles first-run and empty states.

### Cost, honestly

Every delegated role carries its own context, so a full loop burns substantially more tokens than
one thread doing everything. The trade is real, not free. It earns its cost on work that is
long-running, that has to be correct, or that someone returns to later. It is overkill for a
twenty-line script — run the loop for projects, not errands.

---

## Failure Modes

| Symptom | Missed phase |
|---|---|
| "This isn't what I asked for" | 1 — no NOT list |
| "It looks generic / AI-generated" | 2 — stopped at `init`, never rolled a direction |
| "It's beautiful and I can't use it" | 5 — never opened, only reviewed |
| "The whole idea is stubbed" | 5 — stubs never named out loud |
| Design fixes arriving as the last commits | After — audit ran as cleanup instead of before reveal |
| Built the wrong thing fast | 3 — no go/no-go |
| Host constrains a design nobody chose yet | 6 pulled forward into 3 |
| **Plan drift** — the implementer solved a slightly different, easier problem | Build loop — the reviewer checked the code instead of checking it against the plan |
| **Green-washing** — "it works" with nothing executed | Build loop — no command and no output was named |
| **Review theater** — every review returns three medium findings | Build loop — a reviewer that never returns "clean" is performing, not reviewing |
| **Context bleed** — a new topic started in a session full of an old one | Build loop — start fresh; `HANDOFF.md` carries the thread, not the transcript |
