---
name: start-project
description: Kickoff gate for a new project, app, site, or major greenfield feature. Establishes intent and scope, confirms a visual direction or interaction contract, requires explicit approval before product code, and tests a real first run. Use for greenfield work, not ordinary maintenance.
---

# start-project

**Read `METHOD.md` at the Mario root now, and follow it exactly.** Resolve the root from an
explicit absolute path in the coordinator handoff or project instructions, then
`$CLAUDE_PLUGIN_ROOT` when available, the project's `.mario/` pointer, or the current checkout if
it contains `METHOD.md` and `roles/`. Do not search the disk or assume a fixed plugin cache
directory. Report conflicting explicit roots. If none resolves, ask for the Mario path.

`METHOD.md` is the single source of the six phases. This file is only the binding that loads it,
and deliberately does not restate it — a second copy of the method is a second copy to drift.

Two things hold even if that file cannot be read, because they are the ones that get skipped:

- **Create no product root, scaffold, dependencies, or code before Phase 3 approval.** Planning
  artifacts may live outside the intended project root.
- **Nothing is accepted until the real first run is exercised and a human gives a verdict.**
  Agent verification and review evidence are separate from that verdict.

If `METHOD.md` cannot be located, say so and stop. Do not improvise the gate from memory.
