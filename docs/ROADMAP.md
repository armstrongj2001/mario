# Mario workflow overhaul

## User constraints

> I don't want to get rid of the claude Architecture

> I'd just like to add on to it the one we're using Codex

> I don't want to get rid of Astra

> i meant to say the best it possibly can

Preserve Claude's role architecture and tool lists. Claude uses `claude-opus-5-5` for the
architect and implementer, `claude-sonnet-5` for the reviewer, and `claude-haiku-4-5` for
the scribe, with `claude-fable-5-1` available as an opt-in architect. Keep Codex's Astra
architect, Sol implementer, Terra reviewer, and Luna scribe. Improve reliability and
output quality; no cost-minimization mandate. Work in the existing checkout.
No separate Codex fork: both harnesses stay in this repository. On 2026-09-24 the user
authorized completing installation and verification, moving the upgrade through a branch,
merging/pushing main, and writing Obsidian plus Notion session records. This supersedes
the earlier no-commit/no-push constraint.

## Usage scenario

An agent opens a new or existing project in Claude or Codex, loads mario, selects the
appropriate workflow, delegates bounded roles, verifies the actual result, and leaves
records the next session can use. Installation must coexist with user configuration.

## Slices

| Slice | Behavior | Verify by | Status |
|---|---|---|---|
| 1 — Coherent method | Agent can follow kickoff, maintenance, and resumption without contradictory gates or role instructions, including the nonvisual interaction contract and honest empty-state rules. | Independently walk all scenarios in `docs/WORKFLOW-CHECKS.md`; `git diff --check`. | Complete |
| 2 — Usable bindings | Install Claude, Codex, or both safely; diagnose local setup without claiming runtime proof; preserve configured optional integrations and coexist with existing user configuration. | Temporary-directory installer integration tests; shell syntax checks; binding validation; independent review. | Complete; human acceptance pending |
| 3 — Explicit Codex registration | Preserve user settings while registering the four named roles required by the tested client. | Config-preservation regression tests, independent review, live registration check, fresh named architect dispatch. | Complete; named dispatch blocked by client runtime |
| 4 — Current Claude models and Fable opt-in | Pin the four default Claude roles to their current models and offer Fable 5.1 as an explicit architect choice without changing the Codex assignments. | Installer regression tests; source and installed binding diagnostics; dispatched reviewer transcript. | Complete |
| 5 — Optional Notion session notes | Let a project explicitly opt in to local-first Notion closeout notes with verified receipts and duplicate-safe retries, without changing role tools or requiring Notion. | Documentation checks; walk disabled, success, missing connector, incompatible schema, known-page retry, uncertain-create recovery, and ambiguous-match cases; live connected first run. | Agent first run passed; human acceptance pending |

## Acceptance boundaries

- Static configuration validation and filesystem installation do not prove live model routing.
- Fresh-session named-agent discovery is a separate runtime smoke check.
- Human acceptance remains pending until a person tries the intended path and gives a verdict.
- Each implementation slice receives independent review before the next starts.

## Current verification (2026-09-25)

- `python3 -m unittest discover -s tests -q` — 36 tests OK.
- `python3 scripts/doctor.py --source-only --target all` — 29 PASS, 0 FAIL.
- `bash -n scripts/link.sh` and `git diff --check` — exit 0.
- `python3 scripts/doctor.py --target all` — 40 PASS, 0 FAIL after live installation.
- `python3 scripts/register_codex.py --check` — PASS all four Codex agents are registered.
- Optional Notion first run — create/read-back passed; repeat closeout reused the saved page ID,
  and an exact-title query found one page. Human acceptance remains pending.
- See `docs/WORKFLOW-CHECKS.md` for runtime receipts and limits.
