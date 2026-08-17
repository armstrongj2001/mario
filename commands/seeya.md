---
description: End-of-session wind-down — persist durable facts, write the session note, surface loose ends, and print a handoff for tomorrow.
---

# /seeya

Close out the session so tomorrow starts warm. Run all four steps; do not skip to the summary.

## 1. Persist durable facts

Write to `~/.claude/projects/<project>/memory/` anything that will not be obvious later from the
code or git history — decisions and **why**, options rejected, corrections the user made, product
boundaries, external resources. Skip anything the repo already records.

Update `MEMORY.md` with a one-line pointer per new file. Update existing memories rather than
duplicating; delete any this session proved wrong.

## 2. Write the session note

Invoke the `session-note` skill — it owns the Obsidian vault structure and the Session Log index.
Do not hand-roll a note or invent a different path.

## 3. Surface loose ends

Check and report honestly, without fixing anything unasked:
- Uncommitted or untracked work, per repo touched
- Anything built but **not tested** — say so plainly rather than implying it works
- Decisions the user was asked for and never answered
- Anything left deliberately incomplete, and why

## 4. Handoff

Print a short block: where things stand, the single best next action, and any blocker.
Keep it scannable — this is the first thing read tomorrow, likely with no other context.

---

**Tone:** commit-style. No victory lap, no restating the whole session. If something failed or
went untested, that belongs in the handoff more than the wins do.
