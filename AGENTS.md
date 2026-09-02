# mario

**Engineering discipline for AI coding agents.** A kickoff gate that blocks code until scope is
settled, and a `plan → build → review → run it` chain.

This file is the portable entry point. Codex, Cursor, Gemini, Grok, and any other harness that
reads a root instruction file starts here.

## Read these

| File | What it is |
|---|---|
| `METHOD.md` | **The method.** Six phases, the gate, the first-run check. Read it in full. |
| `roles/*.md` | The five roles — architect, implementer, code-reviewer, project-manager, scribe.<br>Claude Code binds all but `project-manager`, which Workforces owns; the scribe binds as `@mario-scribe`. |

Everything else in this repo is a per-harness binding that points at those two. `agents/` is the
Claude Code dialect, `skills/` and `commands/` are its skill and slash-command wiring. If you are
not Claude Code, ignore them — they contain no instructions the files above do not already carry.

## Running the roles without subagent support

Claude Code and Antigravity spawn each role as a separate agent with its own tool set, so the
architect is *unable* to write code. If your harness has native subagents, bind the roles that way
and keep the restriction.

If it does not, run them as sequential passes in one session, and treat the boundary as a hard
rule instead of an enforced one:

1. **Plan** as the architect — output a plan, no code, no files touched.
2. **Build** as the implementer — execute that plan exactly, deviations disclosed.
3. **Review** as the code-reviewer — read the diff adversarially, run the tests yourself.

The weakness is real and worth naming: one model reviewing its own work is not fresh eyes. Where
the harness lets you switch models between steps 2 and 3, do it.

## The build loop, in one paragraph

Work runs one slice at a time. A slice is one behavior a human could verify by running the thing;
if you cannot state its verification step in a sentence, it is too big. Plan the slice, build only
that slice, then review the **diff** against the plan and run the verification independently.
Every claim of success names the command that ran and what it printed. Anything broken outside the
current slice goes to `docs/PUNCHLIST.md` unfixed. Decisions go to `docs/DECISIONS.md`, session
state to `docs/HANDOFF.md` — context does not persist, written records do.

## The two rules that are the whole point

Every other part of this method exists somewhere else. These two do not:

- **The NOT list.** What the product explicitly must never become, captured verbatim at Phase 1 and
  used to settle every later scope question. No brief contains it; you have to ask.
- **The first run.** The app runs on localhost, at the viewport and in the scenario it will really
  be used, and a person completes the primary path with real input before anyone calls it done.
  Craft reviews measure whether a surface is *good*. Only this measures whether it is *usable* —
  and a build can pass a dozen craft reviews with an invisible input and no buttons.
