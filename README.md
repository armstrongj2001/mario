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

Clone it, then preview and install the harness you use:

```bash
git clone https://github.com/armstrongj2001/mario.git && cd mario

bash scripts/link.sh --target claude --dry
bash scripts/link.sh --target claude

bash scripts/link.sh --target codex --dry
bash scripts/link.sh --target codex

# Or install both:
bash scripts/link.sh --target all
```

The first interactive Claude install asks whether to bind the architect to Claude Fable
5.1, which costs more than the default Opus 5.5. Later runs keep the installed choice;
switch with `--fable` or `--no-fable`. Plugin installs use the Opus 5.5 architect.

The default command, `bash scripts/link.sh`, still targets Claude. Claude also supports
its existing plugin installation:

```text
/plugin marketplace add armstrongj2001/mario
/plugin install mario@mario
```

The link installer respects `CLAUDE_HOME` and `CODEX_HOME`, defaulting to `~/.claude`
and `~/.codex`. Use absolute paths for custom homes. Bash and standard Unix filesystem
utilities are required; WSL is suitable on Windows.

Installation creates links back to this checkout. It validates the complete selected
manifest before writing. Existing matching links are kept; other files, directories,
and links are reported as conflicts, with no selected links changed. Review those
conflicts yourself; the installer does not replace another toolkit's agents. Symlinked destination parent directories
are rejected to avoid redirecting writes. Unexpected I/O failures can still interrupt
an install; rerunning it checks the current state.

Preview creates nothing. Uninstall removes only this checkout's matching links and
keeps other entries; it does not create directories:

```bash
bash scripts/link.sh --target codex --unlink
# Use --target claude or --target all as needed.
```

Restart the client after installing or changing its agent configuration. Symlinks keep
the source current; they do not force a running client to reload it.

### Explicit Codex registration

In the tested Codex CLI 0.155.1, installing the TOML files alone did not expose the
named-role configuration. Register it in the existing user configuration as well:

```bash
python3 scripts/register_codex.py --dry
python3 scripts/register_codex.py
python3 scripts/register_codex.py --check
```

Registration exposes role configuration; it does not prove successful dispatch.
The tested client still returned `agent type is currently not available` in a fresh
session after persistent registration. See `docs/WORKFLOW-CHECKS.md` for evidence
and the explicit-model fallback in `codex/AGENTS.md`.

Run this after installing the Codex links. The helper adds only missing
`[agents.<name>]` entries, preserves existing configuration bytes and unrelated
settings, refuses conflicting roles, and creates a private backup before an atomic
replacement. It does not change the configured model assignments. Dry run and check
write nothing. Restart the client, then test named dispatch without command-line
registration overrides. Close other configuration editors while applying: the helper
rechecks the file immediately before replacement, but cannot lock out unrelated
writers during the final check-to-replace interval.

`link.sh --unlink` removes links only; it leaves explicit registrations untouched.
To remove registration, inspect the four role entries and remove only those whose
`config_file` points to these Mario agents. Do not restore an old whole-file backup
over later unrelated configuration changes.

## Connect a project

In the project root, add a `.mario` symlink to this checkout if none exists, and ignore
that local pointer in Git. For example, after checking the path is unused:

```bash
ln -s /absolute/path/to/mario .mario
```

Add `.mario` to the project's existing `.gitignore`. Add this instruction to its
existing root `AGENTS.md`, preserving its other rules:

> This project follows the mario method. Read `.mario/AGENTS.md`.

For Claude or Gemini, add the same pointer to the project's existing `CLAUDE.md` or
`GEMINI.md` as appropriate. Create an instruction file only if missing; do not overwrite
project instructions. When working in this mario checkout itself, its root instructions
already provide the entry point.

The shared entry point loads the method, roles, and applicable harness binding. A pointer
only to `METHOD.md` and `roles/` misses Codex's model-routing instructions. The installer
does not alter project files or configure a remote, vault, editor, or other toolkit.

## Check the setup

```bash
# Validate the checkout without requiring an installation:
python3 scripts/doctor.py --source-only

# Check installed links for the selected harness:
python3 scripts/doctor.py --target codex

# Also inspect a downstream project's .mario and AGENTS.md pointers:
python3 scripts/doctor.py --target all --project /absolute/path/to/project
```

The diagnostic is read-only and returns nonzero for failed checks. Codex TOML checks
use Python 3.11's `tomllib`, or an available `tomli` parser (including pip's bundled
copy on older Python). Nothing is downloaded automatically. Python 3.10 or newer is
required for the diagnostic and tests.

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
