# mario

**Engineering discipline for AI coding agents.**

A kickoff gate that blocks code until scope is settled, and a `plan → build → review` chain where
each agent is restricted to what its job actually needs.

---

## Why

Coding agents fail two ways: they build the wrong thing, and they build the right thing badly.
Both come from starting to write before the target is defined.

Most agent toolkits address this with prose — a persona that *asks* the planner not to write code.
Prose gets ignored under pressure. mario enforces it structurally instead:

```yaml
# agents/architect.md
tools: Read, Grep, Glob     # no Write, no Edit — it physically cannot
```

Three principles, and everything else follows:

1. **Tool restriction is enforcement.** The architect cannot write files. That's a capability
   boundary, not a request.
2. **Tiered models.** Cheap and fast plans, strong implements, independent reviews. Speed without
   accuracy loss comes from matching model to task, not from one model rushing everything.
3. **Review by a different model than authored the code.** Fresh eyes aren't invested in the work.

## How it's laid out

The method is plain prose in files no harness owns. Everything else points at it.

```
METHOD.md      ← the six phases. Platform-neutral. The single source.
roles/*.md     ← the five roles, in prose. Also the source.
AGENTS.md      ← portable entry — Codex, Cursor, Gemini, Grok
agents/*.md    ← Claude Code binding: frontmatter + a pointer. 13 lines each.
skills/ commands/  ← Claude Code skill and slash-command wiring
```

No file restates another, so there is nothing to regenerate and nothing to drift. Editing the
method means editing `METHOD.md`, once.

**What survives the port:** the phases, the gate, the NOT list, the first-run check — all prose,
all portable. **What doesn't:** per-role tool restriction. Claude Code and Antigravity spawn the
architect with no write tools, so it *cannot* produce code. Codex and Cursor have one agent with
one toolset, where that becomes a rule the model is asked to follow. Same words, weaker guarantee —
`AGENTS.md` says so plainly rather than implying the enforcement travels.

## Install

```
/plugin marketplace add armstrongj2001/mario
/plugin install mario@mario
```

Or symlink it for live editing (edits take effect on the next turn, no reinstall):

```bash
git clone https://github.com/armstrongj2001/mario.git ~/mario
bash ~/mario/scripts/link.sh
```

## What's in it

| Agent | Model | Tools | Job |
|---|---|---|---|
| `@architect` | sonnet | Read, Grep, Glob | Plans. **Cannot write files.** |
| `@implementer` | opus | + Write, Edit, Bash | Executes plans exactly. Won't redesign mid-flight. |
| `@code-reviewer` | sonnet | Read, Grep, Glob, Bash | Correctness, security, plan compliance, duplication |
| `@project-manager` | sonnet | + Bash, Write | Backlog, prioritization, GitHub issues |
| `@scribe` | haiku | Read, Grep, Write | Persists decisions and corrections |

| Command | Job |
|---|---|
| `/start-project` | Kickoff gate — intent, scope, design, go/no-go, and a running localhost build a person can use |
| `/seeya` | Wind-down — persist facts, write the session note, surface loose ends, hand off |

## The flow

```
/start-project    1. roadmap — bring one or build one · NOT list · the real usage scenario
                  2. → design, handed to /impeccable end to end (the user locks a direction)
                  3. go/no-go gate  ← cannot be waived
                  4. scaffold · ROADMAP · .env · git · private remote · Workforces · bindings
@architect        plan ONE slice: files, signatures, edge cases, "verify by"
@implementer      build that slice · punchlist anything else · name the command and its output
@code-reviewer    read the diff cold, run the verification, CRITICAL blocks the slice
   ↑ repeat per slice
                  5. FIRST RUN — localhost, real viewport, real scenario  ← blocks the reveal
                  6. deploy target, chosen once something runs
@scribe           persist decisions and corrections
```

Nothing is written to disk until step 3 is approved. Everything in step 4 then runs without
further prompting — approval covers the whole setup.

**Four checkpoints stop and wait for a human**: the roadmap and NOT list, the visual direction,
go/no-go, and the first-run verdict. There is no unattended mode for `/start-project`, deliberately
— a run that completes overnight with nobody awake is the failure this method exists to prevent.

Two steps are load-bearing.

The **NOT list** in step 1 is the question that prevents building the wrong product, and it's the
one nobody asks.

**Step 5** is the one every other toolkit is missing. Craft reviews ask whether a surface is
distinctive, committed, contrast-correct, and free of AI clichés. None of them asks whether a
person can use it — so a screen with an invisible input and no buttons passes a clean sheet. Step 5
opens the app at the size and hour it will actually be used, and any "no" is a blocker.

## Composes with

mario owns engineering discipline only. It deliberately doesn't do design or project management,
and pairs with tools that do:

- **[impeccable](https://github.com/pbakaus/impeccable)** — all design, end to end. Phase 2 hands
  the project over: `init` for product truth, then the direction round, which serves a decision
  page on localhost where the *user* locks a visual direction dealt from a seeded catalog. mario
  ships no design agent of its own, deliberately — a single model's taste converges on the same
  concept every run.
- Any workflow/GitHub toolkit for backlog and planning, installed per-project after the gate.

## Using it with Codex, Cursor, or Grok

Phase 4 sets each project up for this automatically: a gitignored `.mario` symlink at the project
root and a committed three-line `AGENTS.md` pointing into it. A symlink, never a copy — a copy
stops hearing about edits the day it is made.

Manually, in any project:

```bash
ln -s ~/antigravity/mario .mario && echo ".mario" >> .gitignore
```

Then point the tool at `.mario/AGENTS.md`.

## Customizing

To change *what a role does*, edit `roles/<name>.md` — one file, every harness.
To change *how Claude Code runs it*, edit `agents/<name>.md`: its model, or its tools.
If you symlinked, changes are live immediately.

Changing `tools:` changes what an agent *can* do, not just what it's told to do — that's the point.
Adding `Write` to `@architect` removes the guarantee.

```bash
bash scripts/link.sh --dry      # preview
bash scripts/link.sh            # apply
bash scripts/link.sh --unlink   # remove
```

## Status

**v0.8.0 — early.** The structure is verified: agents register, frontmatter parses, tool
restrictions apply at load time. Real-world results across many projects are still being gathered.
Issues and PRs welcome.

## License

MIT
