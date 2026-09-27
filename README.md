Use Mario with your favorite AI coding agent—in your IDE or terminal. [Connect it to your project](#connect-a-project) through the agent’s instruction file, and use the same scope → plan → build → review → run workflow from kickoff through ongoing development.

![Mario warp pipe gate: jumbled code in, star-powered clean code out](docs/mario-gate.gif)

<details>
<summary>The kickoff gate in ASCII</summary>

```text
                                 ___  ___  ___  ______ _____ _____
                                 |  \/  | / _ \ | ___ \_   _|  _  |
                                 | .  . |/ /_\ \| |_/ / | | | | | |
                                 | |\/| ||  _  ||    /  | | | | | |
                                 | |  | || | | || |\ \ _| |_\ \_/ /
                                 \_|  |_/\_| |_/\_| \_|\___/ \___/



                                       No code before scope.

====================================================================================================

            #$%&@#*?!$%&         ──▶  ╔════════════════════╗  ──▶     { settle_scope(); }
            &@#*$%!?#@$%&        ──▶  ║                    ║  ──▶     { plan_slice();   }
             #@%&$#!?*&@         ──▶  ║      KICKOFF       ║  ──▶     { architect();    }
            $%!@#&*?$#&%         ──▶  ║       GATE         ║  ──▶     { implement();    }
             @#$%!&?*#@&         ──▶  ║                    ║  ──▶     { review();       }
            %&#$@!?*#&$%         ──▶  ║   NO SCOPE →       ║  ──▶     { fix();          }
             $#@%&*!?#@&         ──▶  ║   NO CODE          ║  ──▶     { scribe_log();   }
            !@#$%&*?#@$%         ──▶  ║                    ║  ──▶     { ship();         }
             #%&$@#!?*&%         ──▶  ╚════════════════════╝  ──▶

====================================================================================================

              ┌───────────┐      ┌─────────────┐      ┌───────────────┐      ┌────────┐
              │ Architect │ ───▶ │ Implementer │ ───▶ │ Code Reviewer │ ───▶ │ Scribe │
              └───────────┘      └─────────────┘      └───────────────┘      └────────┘

                       coordinator owns scope, dispatch, and the final report

                         mario: engineering discipline for AI coding agents
```

</details>

# mario

Engineering discipline for AI coding agents: settle scope, plan one slice, build it,
review it independently, and run the thing a person will actually use.

Mario supports **Claude Code and Codex side by side**. The shared method and roles
stay the same; each harness has its own model assignments and permission controls.
It is a set of instructions and bindings, not a background pipeline or an enforcement
engine. The coordinator must actually dispatch the roles and show verification evidence.

## The roles

| Role | Responsibility | Claude Code | Codex |
|---|---|---|---|
| Architect | Resolve design decisions and plan consequential changes | Opus 5.5 (Fable 5.1 opt-in) | Astra, high reasoning |
| Implementer | Build the agreed slice and verify it | Opus 5.5 | Sol, high reasoning |
| Code reviewer | Independently check the diff and run meaningful verification | Sonnet 5 | Terra, high reasoning |
| Mario scribe | Persist decisions, corrections, and handoff state | Haiku 4.5 | Luna, medium reasoning |

The coordinator owns scope, dispatch, and the final report. It is not another required
subagent. Backlog management belongs to an installed workflow tool, or the fallback
`roles/project-manager.md`; it does not need to run for every slice.

For consequential work, use the full architect → implementer → reviewer loop. A small,
reversible change may use a written in-thread plan, but still gets independent review.
A separate scribe is useful at milestones; keeping records is always required. For
unresolved material findings or high-risk concerns, a fresh Astra review can supplement
Terra, followed by fixes and a focused re-review. More agents alone do not improve quality.

Exact Codex assignments live in `codex/agents/*.toml` and are listed in
[codex/AGENTS.md](codex/AGENTS.md). Claude models are pinned by ID, with tool lists, in
`agents/*.md`; the opt-in Fable architect lives in `variants/fable/architect.md`.

## Start using it

Requires Python 3.10+. Clone, preview with `--dry`, then install for `claude`, `codex`, or `all`:

```bash
git clone https://github.com/armstrongj2001/mario.git && cd mario
python3 scripts/install.py --target all --dry
python3 scripts/install.py --target all
```

On Windows PowerShell, use `py -3` in place of `python3` here and below. No WSL or admin rights
needed. `bash scripts/link.sh` still works on macOS and Linux and takes the same arguments.

- **Fable architect:** the first interactive Claude install asks whether to use Claude Fable 5.1
  (costs more than the default Opus 5.5). Later runs keep the choice; switch with `--fable` or
  `--no-fable`.
- **Links or copies:** macOS/Linux get symlinks, so edits here are live. Windows gets managed
  copies; rerun the installer after pulling. Force either with `--mode symlink` or `--mode copy`;
  an existing install keeps its mode, and older Mario symlink installs keep working.
- **Homes:** `CLAUDE_HOME` and `CODEX_HOME` override `~/.claude` and `~/.codex`.
- **Safe by default:** nothing is overwritten. Any existing file the installer didn't create is
  reported as a conflict and nothing changes. See [docs/DECISIONS.md](docs/DECISIONS.md) for the
  ownership rules.
- **Uninstall:** `--unlink` removes only what Mario installed and leaves edited copies alone.

Restart the client after installing. Claude can also install as a plugin (Opus architect only):

```text
/plugin marketplace add armstrongj2001/mario
/plugin install mario@mario
```

### Codex registration

Codex CLI 0.155.1 also needs the roles registered in its config:

```bash
python3 scripts/register_codex.py --dry
python3 scripts/register_codex.py
python3 scripts/register_codex.py --check
```

It adds only missing `[agents.<name>]` entries, refuses conflicting ones, and backs up the config
first. Registration doesn't guarantee dispatch; the tested client still reported
`agent type is currently not available`. See [docs/WORKFLOW-CHECKS.md](docs/WORKFLOW-CHECKS.md)
and the explicit-model fallback in [codex/AGENTS.md](codex/AGENTS.md). `--unlink` leaves
registrations in place; to remove them, delete the four entries whose `config_file` points here.

## Update

| Installed with | Update by |
|---|---|
| Installer on macOS/Linux (symlinks) | `git pull`, then restart the client |
| Installer on Windows (copies) | `git pull`, then `py -3 scripts/install.py --target all`, then restart |
| Claude plugin | `/plugin marketplace update mario`, update `mario` from `/plugin`, then restart |

Confirm with `python3 scripts/doctor.py --target all` (0 FAIL). Codex registration points at the
checkout and does not need rerunning. Changes are listed on the
[releases page](https://github.com/armstrongj2001/mario/releases).

## Connect a project

Add one line to the project's root `AGENTS.md` (or `CLAUDE.md` for Claude-only projects), keeping
its existing rules:

```text
This project follows the mario method. Read "/absolute/path/to/mario/AGENTS.md".
```

Alternatively, symlink the checkout as `.mario` (a junction on Windows), add it to `.gitignore`,
and point to `.mario/AGENTS.md`. Point to `AGENTS.md`, not `METHOD.md`: it also loads the roles
and the Codex model routing. The installer never touches project files.

### Optional Notion session notes

A project can opt in to short Notion closeout notes while keeping repository records primary.
This requires an existing connected Notion app or MCP connector; Mario does not install or
authorize one automatically. Claude users can run `/seeya`; in other agents, ask to close the
session using Mario's session-record procedure. Setup, receipt, verification, and duplicate-safe
retry rules are in [docs/NOTION-SESSION-NOTES.md](docs/NOTION-SESSION-NOTES.md).

## Check the setup

```bash
python3 scripts/doctor.py --source-only                   # this checkout only
python3 scripts/doctor.py --target all                    # installed links/copies
python3 scripts/doctor.py --target all --project /path    # plus a project's pointer
python3 scripts/doctor.py --target claude --claude-plugin-root /path   # plugin install
```

Read-only; exits nonzero on any failure.

**A passing diagnostic proves configuration structure, not runtime delegation.** In a
fresh client session, request a small slice using the named architect, implementer,
and reviewer. Inspect the child threads and their results. Record the requested model,
returned agent identifier, and any model metadata the runtime exposes separately. A
child's statement about its own identity is not independent proof of backend routing.
See [docs/WORKFLOW-CHECKS.md](docs/WORKFLOW-CHECKS.md) for acceptance scenarios.

## How work runs

- **New product:** confirm the roadmap and verbatim NOT list, lock a visual direction
  or nonvisual interaction contract, and approve the reconciled scope before product
  code. Pre-gate planning and design previews live outside the product root.
- **Existing project:** restore its constraints and baseline, then plan and implement
  the requested slice. Missing product documents do not trigger a new-project interview.
- **Resuming:** read the handoff and decisions, apply new corrections, and continue.
- **Review:** use a different agent/model where available, include relevant committed,
  staged, unstaged, and untracked changes, and run the verification independently.
- **First run:** exercise the actual UI, command, API, library, or binding with real input.
  Agent evidence and the human's usability verdict are separate. Pending acceptance is
  reported honestly; a clean review cannot supply the human verdict.

The method is in [METHOD.md](METHOD.md). Workforces, a design plugin, external memory,
and editors are integrations, not prerequisites. Use their installed instructions when
configured; otherwise use the method's local fallbacks. Do not fabricate data or hide a
stub to make a first run appear successful. Honest empty states are part of a usable product.

## What is enforced

Claude's architect binding has no write or shell tools. Its reviewer has Bash for tests,
so “do not edit code” is a role instruction, not an absolute filesystem restriction.
Codex's architect defaults to a read-only sandbox; its other roles allow workspace
writes. Parent runtime permission overrides, including bypass mode, can supersede
sandbox defaults. Neither harness's role name alone enforces a model choice.

Codex custom-agent files explicitly select models. If the host only exposes a generic
spawn tool, the coordinator passes explicit model parameters and the role instructions.
Unavailable models are reported, with at most one retry and no silent substitution.
Without subagent/model-switching support, disclose the weaker sequential fallback.
[Official OpenAI documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
describes Codex's native subagents and configuration behavior.

## Maintain the method

| Location | Purpose |
|---|---|
| `METHOD.md`, `roles/*.md` | Shared workflow and role responsibilities |
| `AGENTS.md` | Portable entry point |
| `agents/`, `skills/`, `commands/` | Claude bindings and commands |
| `variants/fable/` | Opt-in Claude Fable 5.1 architect, linked by `link.sh --fable` |
| `codex/` | Codex routing and model/permission bindings |
| `scripts/link.sh`, `scripts/doctor.py` | Installation and structural diagnostics |
| `scripts/register_codex.py` | Explicit Codex role registration for compatible clients |
| `tests/` | Isolated installer, diagnostic, and registration regression tests |
| `docs/` | Decisions, roadmap, acceptance scenarios, and handoff |

Run the verification before handing over a change:

```bash
bash -n scripts/link.sh
python3 -m unittest discover -s tests -v
python3 scripts/doctor.py --source-only --target all
git diff --check
```

Model choices are explicit defaults, not benchmark claims. Keep model tables and the
diagnostic's expected assignments consistent when intentionally changing them. Preserve
append-only decision history. Real runtime discovery and human acceptance should be
recorded separately from source checks and installation tests.

## Credits

[Workforces](https://github.com/wedigcode/workforces) by wedigcode is the workflow and
backlog toolkit mario is built to sit alongside. It is optional; mario falls back to its own
records when Workforces is not installed.

MIT licensed.

---

## The kickoff gate

![Mario kickoff gate pixel art](docs/mario-hero-pixel.png)
