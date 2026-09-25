---
description: End-of-session wind-down — persist durable facts, write the session note, surface loose ends, and print a handoff for tomorrow.
---

# /seeya

Close out the session so tomorrow starts warm. Run all four steps; do not skip to the summary.

## 1. Persist durable facts

Write durable decisions, corrections, boundaries, and open threads to the repo records described
in `METHOD.md`. The repository records are authoritative. Configured external notes may carry a
secondary copy of the same durable facts without expanding the session's scope.

Update existing notes rather than duplicating them.

## 2. Write the session note

The in-repo `docs/HANDOFF.md` is the primary session note. If a session-note skill or vault is
configured, use its instructions too. If the active project opts in to Notion, follow
[`docs/NOTION-SESSION-NOTES.md`](../docs/NOTION-SESSION-NOTES.md) after the local records are
current. Missing configuration, authorization, connector tools, destination, or usable schema
blocks only the external note; report it and finish the local closeout.

## 3. Surface loose ends

Check and report honestly, without fixing anything unasked:
- Uncommitted or untracked work, per repo touched
- Anything built but **not tested** — say so plainly rather than implying it works
- Decisions the user was asked for and never answered
- Anything left deliberately incomplete, and why

## 4. Handoff

Print a short block: where things stand, the single best next action, and any blocker.
Keep it scannable — this is the first thing read tomorrow, likely with no other context. Include
the external-note receipt status and page ID or URL when known, or the external blocker.

---

**Tone:** commit-style. No victory lap, no restating the whole session. If something failed or
went untested, that belongs in the handoff more than the wins do.
