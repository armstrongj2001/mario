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
- **Answer from the prompt before asking.** A good brief already contains most of Phase 1 — extract
  what is there, reflect it back for confirmation, and ask only about what is genuinely missing.
  Re-asking what the user already told you is the fastest way to make this feel like a form.
- **Never skip Phase 2, and never run only part of it.** `/impeccable init` is the first step of
  the design arc, not the whole of it.
- **Never call it done on a passing review.** Craft reviews measure whether a surface is good.
  Only Phase 5 measures whether a person can use it, and it is the one that has been skipped.
- **Do not reproduce copyrighted material.** Reference the structure and pacing of existing
  products; write original content.

---

## Phase 1 — Intent

Write nothing yet. A pasted brief or roadmap is **input**, not approval — briefs describe features
and feel, rarely who it is for or what it must not become.

Extract from what the user already gave you, then confirm and fill gaps. The four things you need:

1. **What is it?** One sentence a stranger would understand.
2. **Who opens it, and what do they do in the first 30 seconds?**
3. **What does it explicitly NOT do?** ← the scope boundary. Force a real answer.
4. **Success looks like…?** A screenshot, signups, a demo?

Ask only for what the brief did not already answer. **Q3 is almost never in a brief** — people
describe what they want, not what they are refusing. Expect to ask it, and expect the first answer
to be vague. Push once with a concrete wrong-direction guess: *"So it is not just a feed of your
GitHub repos?"*

Record the **NOT list** verbatim. Every later scope question is settled against it.

Capture the **real usage scenario** with it — where the user is, on what device, at what hour, in
what state of mind. Phase 5 tests against that scenario, so a vague answer here produces a build
verified in conditions nobody will ever be in.

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

   **The user locks a card. You do not pick for them.** They may re-roll, or steer *safer* /
   *bolder*. Record the seed; it reproduces the entire round.
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

Ask for explicit go/no-go.

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
3. **`README.md`** — what it is and **how to run it locally**. Written for someone returning in six
   months with no memory of it. Deployment is added in Phase 6, once there is a target.
4. **`CLAUDE.md`** — project-specific instructions. Mirror to `AGENTS.md` when other tools are in
   play; keep them identical rather than letting them drift.
5. **`git init`**, then a first commit containing the scaffold only.
6. **Create the remote** — `gh repo create <name> --private --source=. --remote=origin --push`.
   **Private unless the user explicitly asked for public.**
7. **Obsidian** — create `<Project Name>/` in the vault root
   (`/mnt/c/Users/jobid/OneDrive/Documents/X posts/`) with an index note holding the one-liner,
   the NOT list, the locked direction and seed, the repo URL, the local path, and the run command.
   > The vault is under OneDrive. Never run recursive scans (`find`, `grep -r`, `rg`, `ls -R`,
   > `du`) against that path from WSL — it hydrates cloud placeholders and fills the C: drive.
   > Use `powershell.exe -NoProfile -Command "Get-ChildItem ..."` for discovery. Reading and
   > writing individual known files is fine.
8. **Offer to open it.** Ask which editor unless the user has a configured preference — check
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

9. **Portable bindings.** So the method survives whatever tool opens this repo next:
   - A gitignored `.mario` symlink at the project root pointing at the mario checkout. A symlink,
     never a copy — a copy stops hearing about edits the day it is made.
   - `AGENTS.md` (three lines, committed): what the project is, and *"This project follows the
     mario method. Read `.mario/METHOD.md` and the role definitions in `.mario/roles/`."*
     Codex, Cursor, Gemini, and Grok all read a root instruction file; this is the one they get.
   - Add `.mario` to `.gitignore`.
10. **Report** the repo URL, local path, and vault path together.

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

```
@architect                    plan — files, signatures, edge cases, checkpoint test
@implementer                  build the plan exactly
/impeccable audit <surface>   deterministic rules — a11y, contrast, responsive
/impeccable critique <surface> hierarchy, clarity, resonance
@code-reviewer                correctness, security, plan compliance, duplication
Phase 5                       run it, use it, screenshot it   ← blocks the reveal
@scribe                       persist decisions and corrections
```

Run `/impeccable audit` **before** showing the user a surface, not after they complain.
Never ship an empty or placeholder state — `/impeccable onboard` handles first-run and empty states.

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
