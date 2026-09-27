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

Mario's setup tools require Python 3.10 or newer; Python 3.11+ is recommended. Clone the
repository, then preview and install the harness you use.

macOS and Linux:

```bash
git clone https://github.com/armstrongj2001/mario.git && cd mario

python3 scripts/install.py --target claude --dry
python3 scripts/install.py --target claude

python3 scripts/install.py --target codex --dry
python3 scripts/install.py --target codex

# Or install both:
python3 scripts/install.py --target all
```

Native Windows PowerShell:

```powershell
git clone https://github.com/armstrongj2001/mario.git
Set-Location mario
py -3 scripts/install.py --target all --dry
py -3 scripts/install.py --target all
```

The first interactive Claude install asks whether to bind the architect to Claude Fable
5.1, which costs more than the default Opus 5.5. Later runs keep the installed choice;
switch with `--fable` or `--no-fable`. Plugin installs use the Opus 5.5 architect.

The default target remains Claude. On macOS and Linux, `bash scripts/link.sh` is an executable
compatibility launcher for the Python installer and preserves the same arguments. Claude also
supports plugin installation; version 0.9.1 contains the native setup and diagnostic update:

```text
/plugin marketplace add armstrongj2001/mario
/plugin install mario@mario
```

Update or reinstall the plugin and restart Claude after this patch so its cached content reloads.

The installer respects `CLAUDE_HOME` and `CODEX_HOME`, defaulting through the native user home.
Use absolute paths for custom homes. `--mode auto` creates symlinks on macOS/Linux and managed
copies on Windows. Use `--mode copy` or `--mode symlink` explicitly when needed. An existing
install keeps its mode; changing modes requires uninstalling that target first. Legacy Mario
symlinks remain valid.

Every selected target is preflighted before files change. Existing foreign entries, redirected
parents, malformed ownership receipts, case-folded destination aliases, and same-content files
without ownership are conflicts. Receipt paths use `/`; backslashes, repeated separators, and
components ending in a space or dot are rejected instead of normalized.
Copy installs keep `.mario-install.json` in each harness home with source paths and byte hashes.
Rerunning refreshes an owned copy only while its installed bytes still match the prior receipt;
the diagnostic reports stale copies until refresh succeeds. An interrupted filesystem operation
can leave partial unowned files, which Mario reports rather than adopting automatically. Setup
rechecks paths immediately before mutation, but it cannot lock out an unrelated writer during the
final check-to-replace, check-to-link, or check-to-remove interval. The receipt is trusted local
inventory, and its hashes check consistency rather than authenticate provenance. Protecting
against deliberate receipt tampering inside the allowed `skills/start-project` namespace would
require separately protected provenance and is outside this setup format.

Preview creates nothing. Uninstall removes only this checkout's matching links and
unmodified owned copies. It preserves foreign files, locally modified copies, and unrelated files
inside managed directories:

```bash
python3 scripts/install.py --target codex --unlink
# Use --target claude or --target all as needed.
```

On Windows, use `py -3 scripts/install.py --target codex --unlink`. Restart the client after
installing or changing its configuration. Symlinks expose source changes immediately; managed
copies require rerunning the installer. Neither mode forces a running client to reload.

### Explicit Codex registration

In the tested Codex CLI 0.155.1, installing the TOML files alone did not expose the
named-role configuration. Register it in the existing user configuration as well:

```bash
python3 scripts/register_codex.py --dry
python3 scripts/register_codex.py
python3 scripts/register_codex.py --check
```

On Windows, replace `python3` with `py -3`.

Registration exposes role configuration; it does not prove successful dispatch.
The tested client still returned `agent type is currently not available` in a fresh
session after persistent registration. See `docs/WORKFLOW-CHECKS.md` for evidence
and the explicit-model fallback in `codex/AGENTS.md`.

Run this after installing the Codex bindings. The helper accepts verified managed copies,
Mario-owned links, and an existing valid registration that points directly to this checkout. It
adds only missing `[agents.<name>]` entries, preserves existing configuration bytes and unrelated
settings, refuses conflicting roles, and creates a private backup before an atomic
replacement. It does not change the configured model assignments. Dry run and check
write nothing. Restart the client, then test named dispatch without command-line
registration overrides. Close other configuration editors while applying: the helper
rechecks the file immediately before replacement, but cannot lock out unrelated
writers during the final check-to-replace interval.

On POSIX, new configs and backups use private mode `0600`, while an existing config keeps its
mode. On Windows, new files and backups inherit the destination directory's ACL. The helper
refuses read-only configs and redirected mutation paths; it never changes permissions to make a
read-only config writable.

Installer `--unlink` removes owned bindings only; it leaves explicit registrations untouched.
To remove registration, inspect the four role entries and remove only those whose
`config_file` points to these Mario agents. Do not restore an old whole-file backup
over later unrelated configuration changes.

## Connect a project

Point the project's instruction file to the absolute `AGENTS.md` in the Mario checkout. This is
the preferred native Windows setup and also works on macOS and Linux. Preserve existing project
instructions:

```text
Read "C:\dev\mario\AGENTS.md".
```

Quoted or backtick-wrapped paths may contain spaces. For Codex or cross-agent use, put the pointer
in the project's root `AGENTS.md`. Claude-only projects may use either `AGENTS.md` or `CLAUDE.md`.
The referenced checkout is validated by its actual files and may differ from the checkout running
the diagnostic or from a Claude plugin cache.

The portable `.mario` pointer remains supported but is optional. On macOS/Linux, after checking
the path is unused:

```bash
ln -s /absolute/path/to/mario .mario
```

Add `.mario` to the project's existing `.gitignore`. Add this instruction to its
existing root `AGENTS.md`, preserving its other rules:

> This project follows the mario method. Read `.mario/AGENTS.md`.

For Claude or Gemini, the same pointer may also go in the existing `CLAUDE.md` or `GEMINI.md`.
Create an instruction file only if missing; do not overwrite project instructions. A valid
Windows junction is accepted as `.mario`, but no junction is required for an absolute pointer.
When working in this Mario checkout itself, its root instructions already provide the entry point.

The shared entry point loads the method, roles, and applicable harness binding. A pointer
only to `METHOD.md` and `roles/` misses Codex's model-routing instructions. The installer
does not alter project files or configure a remote, vault, editor, or other toolkit.

### Optional Notion session notes

A project can opt in to short Notion closeout notes while keeping repository records primary.
This requires an existing connected Notion app or MCP connector; Mario does not install or
authorize one automatically. Claude users can run `/seeya`; in other agents, ask to close the
session using Mario's session-record procedure. Setup, receipt, verification, and duplicate-safe
retry rules are in [docs/NOTION-SESSION-NOTES.md](docs/NOTION-SESSION-NOTES.md).

## Check the setup

```bash
# Validate the checkout without requiring an installation:
python3 scripts/doctor.py --source-only

# Check installed managed links or copies for the selected harness:
python3 scripts/doctor.py --target codex

# Also inspect a downstream project's instruction pointer:
python3 scripts/doctor.py --target all --project /absolute/path/to/project

# Validate supplied Claude plugin content without requiring home-directory links:
python3 scripts/doctor.py --target claude --claude-plugin-root /resolved/plugin/root
```

Use `py -3` and native Windows paths in PowerShell. `--claude-plugin-root` validates the supplied
plugin's manifest version and source structure, then skips Claude home-link checks; it does not
prove that the client enabled or ran the plugin. The checkout running doctor, supplied plugin
root, and checkout referenced by a project are validated independently and may differ.

The diagnostic is read-only and returns nonzero for failed checks. Codex TOML checks use Python
3.11's `tomllib`, or an available `tomli` parser (including pip's bundled copy on Python 3.10).
Nothing is downloaded automatically.

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
