---
name: start-project
description: Mandatory kickoff gate for any new project, app, site, or major greenfield feature. Establishes intent and scope, hands design to /impeccable, gates on a running localhost build a person can actually use, and requires explicit approval before any code. Use when starting a new project, scaffolding a repo, building a new site or app, or when the user says start a project, new project, build me a, or pastes a roadmap.
---

# start-project

**Read `METHOD.md` at the mario root now, and follow it exactly.** Resolve the root in this order —
`$CLAUDE_PLUGIN_ROOT`, the project's `.mario/` symlink, then `~/antigravity/mario`.

`METHOD.md` is the single source of the six phases. This file is only the binding that loads it,
and deliberately does not restate it — a second copy of the method is a second copy to drift.

Two things hold even if that file cannot be read, because they are the ones that get skipped:

- **Create nothing before the Phase 3 gate is approved.** Not a directory, not a `package.json`,
  not a "quick scaffold to hold things."
- **Nothing is done until it runs on localhost and a person uses it.** A passing review is not a
  substitute for opening the app.

If `METHOD.md` cannot be located, say so and stop. Do not improvise the gate from memory.
