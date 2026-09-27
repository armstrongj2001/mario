# Workflow acceptance scenarios

Walk these against the method, role definitions, entry points, and bindings together.
For each, report the route, evidence, and any conflicting instruction. These are
behavioral review cases, not assertions that matching a phrase proves agent compliance.

| Scenario | Input | Expected behavior |
|---|---|---|
| New web app | Idea only; no NOT list or approved direction | Human intent/direction/go checkpoints run. Planning and disposable design previews stay outside the product root until go. No product scaffold before go. Actual browser path and human verdict follow implementation. |
| New CLI | Explicit command-line product; no visual surface | Preserve intent and go checkpoints; agree command/input/output/error contract instead of inventing three visual directions. Run the command with real input, including failure behavior; human acceptance remains explicit. |
| Existing bug fix | Existing repository, missing PRODUCT.md; bounded authorized fix | Read current state and constraints, choose lane by impact, record baseline and plan. No greenfield interview or scaffold. Do not reset/reinitialize user work. |
| Resume | Handoff and recorded approvals exist; new user correction arrives | Restore records, apply correction, check actual state, continue unfinished slice. Reopen only the decision invalidated by the correction. |
| Small configuration change | Reversible internal setting with a precise expected effect | In-thread short-loop plan is valid. Implementer does not demand a separate architect. Reviewer independently checks the actual effect; security/deployment-sensitive configuration goes full loop. |
| Missing integrations | No Workforces, vault, design plugin, or configured remote | Local work still runs. Use repo records and documented fallbacks; do not create personal directories, install arbitrary tooling, or delete toolkit files. |
| Awaiting acceptance | Tests/review pass but no person has tried the result | Show the running artifact and evidence, state what remains unverified, and await the human verdict. Never label agent verification as human acceptance. |
| Review with existing changes | Dirty working tree, untracked new file, changes committed during slice | Record and use the slice baseline. Include relevant committed/staged/unstaged/untracked changes without attributing pre-existing user work to the implementer. Report any coverage limits. |
| Failed model dispatch | Configured role model returns capacity error | Report the failed handoff. Bound retries; request or use an explicitly authorized replacement. Never claim the role ran or silently switch models. |
| Useful empty state | Real account has zero records | Explain the state and offer a working next action. Demo fixtures are labeled and do not stand in for the core functionality. |
| Native Windows setup | Non-admin PowerShell, no symlink privilege | Native Python defaults to managed copies, records ownership, diagnoses the installed bytes, and uninstalls only unchanged owned files. No Bash, WSL, or elevation requirement. |
| Copy refresh and conflict | Source changed; installed copy unchanged or locally modified | Refresh the unchanged owned copy after full preflight. Refuse a modified or same-content unowned destination; uninstall preserves it. Never infer ownership from content. |
| Claude plugin project | Plugin content and project checkout are distinct; project has only `CLAUDE.md` with an absolute Mario `AGENTS.md` path | Validate plugin structure/version separately from the referenced checkout. Accept the verified absolute project pointer without requiring `.mario` or Claude home links. Do not claim plugin enablement or runtime routing. |
| Portable project route | Codex or all-target project check | Require root `AGENTS.md`; accept `.mario/AGENTS.md` or an exact absolute path to a real compatible checkout. A mere `AGENTS.md` substring is not a route. |
| Representation preservation | Existing file uses BOM, CRLF, or nondefault mode | Implementer inspects and preserves bytes/newlines/mode outside the intended edit; reviewer compares representation with baseline. No bulk normalization. |

## Runtime checks after installation

1. Open a fresh client session in a project pointing to Mario through `.mario/AGENTS.md` or a
   verified absolute checkout `AGENTS.md` path.
2. Request a bounded planning task and an independent review with named roles.
3. Inspect the returned thread identifiers and model metadata the client exposes.
4. Record configured/requested model separately from observed runtime metadata.
5. Exercise a small real change through plan, implementation, review, and its Verify by step.

No self-reported model identity, parsed TOML, or symlink check can substitute for these steps.

## 2026-09-24 installation and runtime receipts

- CLI: `codex-cli 0.155.1`. Live `bash scripts/link.sh --target all` retained seven
  correct Claude links and installed four Codex links.
- `python3 scripts/doctor.py --target all`: **39 PASS, 0 FAIL**. This validates
  files and links only.
- `python3 scripts/register_codex.py`: registered all four roles and created
  `~/.codex/config.toml.mario-backup` with private permissions.
- `python3 scripts/register_codex.py --check`: **PASS all four Codex agents are registered.**
- `python3 -m unittest discover -s tests -q`: **34 tests, OK**, independently rerun
  by the reviewer. Includes conflict, byte preservation, backup permissions,
  idempotence, redirected path, relative path and concurrent-change cases.
- Fresh read-only `codex exec --ephemeral --sandbox read-only --json -C <mario>`
  with a prompt to dispatch the installed `architect` by name, without model overrides:
  runtime listed architect/Astra/high, then returned **agent type is currently not available**.
  No spawn ID was returned. Local receipt: `/tmp/mario-persistent-smoke.jsonl`;
  final response: `/tmp/mario-persistent-smoke-result.txt`.
- An earlier run with explicit `-c agents.architect.config_file=...` reported
  `/root/architect_runtime_test`, but its event stream contained no raw spawn event
  and only an empty-recipient wait. Treat that as a subprocess report, not independent
  proof that named dispatch succeeded. It does not overturn the observed failure.

The current session used native delegated roles for planning, implementation, and
independent review. That demonstrates the explicit delegation path in this session,
not automatic named-agent discovery in every client or backend identity attestation.
Human acceptance of a complete downstream project workflow remains pending.

The final bounded repeat using the direct repository path again reported a child
result without a raw spawn event (empty-recipient wait only). It remains inconclusive;
no path-format fix is justified by this evidence. Diagnosis stopped for this session.

## 2026-09-26 native-platform receipts

- Native Windows 11, non-admin Python 3.12 on NTFS paths with spaces: the latest 44-test snapshot
  passed with six narrow OS-specific skips. A full native lifecycle also passed:
  managed-copy install and repeat, source and installed doctor, Codex registration/check/repeat,
  absolute project pointers, Fable switches, selective uninstall, and plugin-only diagnostics.
- Windows diagnostic receipts: source **32 PASS, 0 FAIL**; installed all-target **43 PASS,
  0 FAIL**; project all-target **47 PASS, 0 FAIL**; plugin-only Claude project **46 PASS,
  0 FAIL**. Plugin output identified version 0.9.1 and kept content checks distinct from runtime
  enablement. A drive-qualified malformed receipt was rejected and its outside sentinel remained
  unchanged.
- Local Linux after the final test additions: `python3 -m unittest discover -s tests -q` —
  **51 tests OK**, one Windows-only junction test skipped; source doctor **32 PASS, 0 FAIL**;
  shell syntax and `git diff --check` exited 0. Focused independent re-review remains pending.
- macOS execution and hosted CI matrix results remain pending. These Windows/Linux receipts do
  not certify macOS, live plugin enablement, named-role dispatch, backend model identity, or a
  human usability verdict for the new setup path.
