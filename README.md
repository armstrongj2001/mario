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
| `@architect` | fable | Read, Grep, Glob | Plans. **Cannot write files.** |
| `@implementer` | opus | + Write, Edit, Bash | Executes plans exactly. Won't redesign mid-flight. |
| `@code-reviewer` | sonnet | Read, Grep, Glob, Bash | Correctness, security, plan compliance, duplication |
| `@design-pilot` | fable | + WebFetch | Visual direction from real references, never imagination |
| `@design-reviewer` | sonnet | Read, Grep, Glob | Gates UI before the user sees it |
| `@project-manager` | sonnet | + Bash, Write | Backlog, prioritization, GitHub issues |
| `@scribe` | haiku | Read, Grep, Write | Persists decisions and corrections |

| Command | Job |
|---|---|
| `/start-project` | Kickoff gate — intent, scope, design context, explicit go/no-go before any code |
| `/seeya` | Wind-down — persist facts, write the session note, surface loose ends, hand off |

## The flow

```
/start-project    1. what is it · who · what it does NOT do · success
                  2. → design context
                  3. go/no-go gate  ← cannot be waived; names the deploy target
                  4. scaffold · .env · README · git · private remote · notes
@architect        plan: files, signatures, edge cases, checkpoint test
@implementer      build the plan exactly
@code-reviewer    correctness, security, duplication
@scribe           persist decisions and corrections
```

Nothing is written to disk until step 3 is approved. Everything in step 4 then runs without
further prompting — approval covers the whole setup.

The **NOT list** in step 1 is the load-bearing part. "What does this explicitly not do?" is the
question that prevents building the wrong product, and it's the one nobody asks.

## Composes with

mario owns engineering discipline only. It deliberately doesn't do design or project management,
and pairs with tools that do:

- **[impeccable](https://github.com/pbakaus/impeccable)** — design. `/start-project` hands off to
  `/impeccable init` for design context, and `/impeccable audit` gates surfaces before reveal.
  With it installed, retire `@design-pilot` and `@design-reviewer`.
- Any workflow/GitHub toolkit for backlog and planning.

Neither is required. Without them, the included design agents cover the gap.

## Customizing

Everything is a Markdown file with YAML frontmatter. Edit `agents/*.md` to change a role, its
model, or its tools. If you symlinked, changes are live immediately.

Changing `tools:` changes what an agent *can* do, not just what it's told to do — that's the point.
Adding `Write` to `@architect` removes the guarantee.

```bash
bash scripts/link.sh --dry      # preview
bash scripts/link.sh            # apply
bash scripts/link.sh --unlink   # remove
```

## Status

**v0.3.0 — early.** The structure is verified: agents register, frontmatter parses, tool
restrictions apply at load time. Real-world results across many projects are still being gathered.
Issues and PRs welcome.

## License

MIT
