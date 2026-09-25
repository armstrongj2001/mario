# Handoff

## 2026-09-24 — Claude and Codex overhaul

- Delivery: implementation commit `a8209f9` reviewed on `upgrade/claude-codex-workflow`,
  fast-forwarded into main and pushed to origin. Seven earlier local commits preserved.
  Post-push comparison: 0 ahead, 0 behind; working tree clean. No separate fork or release tag.
- Done: coherent greenfield/maintenance/resume routes; scope and human checkpoints
  preserved; bounded native-role handoffs; explicit model selection/failure handling;
  nonvisual first runs; safe dual-harness installation, diagnostics and Codex registration.
- Claude architecture, model assignments and tool lists preserved. Codex configuration:
  Astra architect (`gpt-6-astra`), Sol implementer (`gpt-5.6-sol`), Terra reviewer
  (`gpt-5.6-terra`), Luna scribe (`gpt-5.6-luna`). No silent model substitutions.
- Live setup: seven existing Claude links correct; four Codex links installed; all four
  roles registered in user config. Private backup: `~/.codex/config.toml.mario-backup`.
- Verification: `python3 -m unittest discover -s tests -q` — 34 tests OK;
  `python3 scripts/doctor.py --target all` — 39 PASS, 0 FAIL;
  `python3 scripts/register_codex.py --check` — PASS all four registered;
  `bash -n scripts/link.sh` and `git diff --check` — exit 0.
- Review: independent Terra review clean, including final config-concurrency fix.
  Helper detects tested concurrent changes and documents the residual final race.
- Runtime limit: CLI 0.155.1 lists registered architect metadata but persistent named
  dispatch returned `agent type is currently not available`. Two explicit launch-override
  runs reported a child result but lacked raw spawn events; named dispatch remains
  unverified. See WORKFLOW-CHECKS.md and PUNCHLIST.md. Do not report all-role runtime
  certification or backend identity attestation.
- Acceptance: no human verdict on a complete downstream workflow yet. This is distinct
  from code review, installation checks and delegated work in this session.
- Next chat: read this file and `codex/AGENTS.md`; use supported explicit model/role
  dispatch when named dispatch fails. Resume client integration diagnosis only if
  requested; do not redo the overhaul, create a fork, remove Astra or replace Claude.
- User correction: quality was the objective (“best it possibly can”), not token cost.
  User wants the session closed after delivery and notes; avoid reopening scope.
- Session records written and read back: Obsidian
  `Sessions/2026-09-21 Mario — Claude and Codex Upgrade.md` (session closed 2026-09-24),
  with Session Log index entry; [detailed Notion rundown](https://app.notion.com/p/3e597c6ead7c8116b93bc7ea92536807)
  under Coding Projects → Notes. This final documentation commit records those receipts.

## 2026-09-25 — Claude models pinned; Fable opt-in

- Claude bindings: architect and implementer `claude-opus-5-5`, reviewer `claude-sonnet-5`,
  scribe `claude-haiku-4-5`; opt-in `claude-fable-5-1` architect via `link.sh --fable`.
  This supersedes "Claude model assignments preserved" above.
- Runtime evidence: a dispatched code-reviewer's transcript recorded every response from
  `claude-sonnet-5`. Other roles not runtime-checked.
- Verification: 36 tests OK; doctor `--source-only --target all` 29 PASS; fresh GitHub clone
  installed into an isolated home, doctor `--target all` 40 PASS.

## 2026-09-25 — Roadmap refresh

- Updated `docs/ROADMAP.md` to record the completed pinned-model/Fable slice and current
  verification counts while preserving the pending human acceptance and named-dispatch failure.
- Committed and pushed to main with the README art commits.

## 2026-09-25 — README entry point

- User wants IDE/terminal use and bring-your-own coding-agent setup prominent in the README.

## 2026-09-25 — Optional Notion closeout notes

- Added the local-first Notion opt-in contract and wired it into the method, scribe, `/seeya`,
  and README. Agent first run passed: create read-back confirmed parent, session key, and content;
  repeat closeout fetched and updated the same saved page; exact-title query returned one page.
  Private destination and page identifiers remain in the ignored local receipt.
- Uses the existing connector without new SDKs, secrets, personal IDs, schema changes, or
  expanded scribe tools. The user wants a multi-provider router kept as an idea only.
- Requested role identities, not backend attestation: planner `/root/notion_plan` on Astra;
  implementer `/root/refresh_roadmap` on Sol; reviewer `/root/review_claude_fallback` on Terra.
- Independent Terra review clean; `python3 -m unittest discover -s tests -q` — 36 tests OK;
  `python3 scripts/doctor.py --source-only --target all` — 29 PASS, 0 FAIL;
  `git diff --check` — exit 0. Human acceptance remains pending.
- Concurrent Claude commit `e52f34e` captured the initial tracked changes; final guide and
  receipt refinements complete locally. No push performed by this task.
- Next closeout: read the project's ignored session-note configuration, refresh local records,
  and publish through the connected Notion tools using the saved receipt for retries.
