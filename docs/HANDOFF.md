# Handoff

## 2026-09-24 — Claude and Codex overhaul

- Delivery: reviewed on `upgrade/claude-codex-workflow` in the existing Mario repo;
  user authorized fast-forward/push to main and Obsidian/Notion closeout. No separate fork.
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
