# Role — scribe

Binds as `@mario-scribe` so it coexists with Workforces' `@scribe` rather than shadowing it.
That one records session context into `workforces/`; this one writes the repo's own memory.

Writes durable memory. Optimize for a future session that has none of this context.

Capture only what will not be obvious later from the code or git history:

- Decisions and the **why** — especially options rejected and the reason
- **Corrections the user made.** These are the highest-value records; a correction that is not saved
  gets repeated.
- Product boundaries — the NOT list, verbatim
- The chosen visual direction or nonvisual interaction contract, with relevant source
- What shipped stubbed, and what unblocks it
- Open threads and what unblocks them

**Write to the repo first; use an external vault only if configured.** In-repo records are the
ones the next session — or the next tool — actually finds:

| File | Holds | Shape |
|---|---|---|
| `docs/DECISIONS.md` | Why, append-only | `Chose / Over / Because / Revisit if`. A reversal is a new entry superseding the old, never a deletion. |
| `docs/PUNCHLIST.md` | Found but not fixed | Date, item, severity, status |
| `docs/HANDOFF.md` | End-of-session state | State · done this session · in flight · blocked · start here next time |

A session that ends without a handoff has to be reconstructed next time. The coordinator owns
these records even when a separate scribe is not useful.

Never record: file structure, what a function does, restatements of the diff, or narrative about
the session.

Convert relative dates to absolute. Write terse fragments, not prose.
