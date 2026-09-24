---
description: End-of-session wind-down — persist durable facts, write the session note, surface loose ends, and print a handoff for tomorrow.
---

# /seeya

Close out the session so tomorrow starts warm. Run all four steps; do not skip to the summary.

## 1. Persist durable facts

Write durable decisions, corrections, boundaries, and open threads to the repo records described
in `METHOD.md`. Use configured external memory only for details the repo should not hold.

Update existing notes rather than duplicating them.

## 2. Write the session note

If a session-note skill or vault is configured, use its instructions. Otherwise the in-repo
`docs/HANDOFF.md` is the session note.

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
