# The mario Method

*Shared method for every harness. `AGENTS.md` and role bindings point here.*

Mario settles scope before a new product is built, then runs one verifiable slice through
`plan → build → review → run it`. Preserve the user's existing work and instructions. The NOT
list is the explicit product boundary; a real first run tests whether the result can be used.

## Choose the route first

| Work | Route |
|---|---|
| New product, app, site, or similarly open-ended greenfield feature | Phases 1–6. The Phase 3 gate applies to product code, scaffolding, dependencies, and project-root creation. |
| Change to an existing product, including a bug fix or refactor | Read its instructions and records, establish the baseline, then use the build loop for the requested slice. Reuse existing product decisions; ask only when the change crosses an unresolved boundary. |
| Resumed work | Read `docs/HANDOFF.md`, `docs/ROADMAP.md`, decisions, and any pending planning artifact first. Confirm what was already decided and continue at the applicable phase. Do not restart the interview or repeat an answered checkpoint. |

An explicit user request to modify this method or an existing repository is maintenance work. A
project's own instructions and the user's current scope control its implementation.

## Operating rules

- Announce the route and important handoffs. Use available native agents when configured;
  otherwise run explicit sequential role passes. The coordinator owns the chain. A delegated
  role does its bounded assignment and returns; it does not recursively start another chain.
- One writer owns each file in a slice. Record the agreed baseline before work: branch/commit,
  staged and unstaged changes, and relevant untracked files. Preserve pre-existing user work.
- Use configured design tools, Workforces, vaults, editors, and remotes when useful and available.
  Their absence does not stop the method. No fixed personal path, tool command, or account is a
  requirement. Never delete existing toolkit or instruction files to resolve a conflict; report
  the conflict and make the smallest safe change within the agreed scope.
- Do not reproduce copyrighted content. References may inform structure and pacing; create
  original copy, assets, and identity.
- Carry one bounded handoff between roles: route and slice, agreed scope and NOT list, files to
  touch, baseline, exact **Verify by** step, required artifacts, constraints, and unresolved
  decisions. Update it when the user changes scope.

## Phase 1 — Roadmap and intent (greenfield)

First reflect what the user has already supplied. Ask where a roadmap comes from only if unclear:
one they provide, or one to make together. A supplied roadmap is input, not automatic approval.
Reconcile its answers, gaps, and conflicts with the user. Ask in compact rounds, grouping related
questions rather than re-asking answered ones.

Settle four things: what it is; who uses it and what they first do; what it explicitly **must not
become**; and what success looks like. Ask for a concrete NOT list if none was supplied. Capture
the real use scenario, including device or environment and the user's context. Show the roadmap,
NOT list verbatim, use scenario, and any conflicts together for correction. **Checkpoint 1:** a
human confirms them. If the answer is missing, wait; do not infer it.

Before Phase 3, planning artifacts may be written only in an external planning workspace or
harness scratchpad, outside the intended product root. This includes PRODUCT/DESIGN notes,
reference assets, and disposable design previews. Preserve confirmed answers there so a resumed
session does not re-interview the user. This exception does not permit a product directory,
scaffold, dependency install, or product code.

## Phase 2 — Design or interaction contract (greenfield)

For a visual surface, use the actual installed design tool's instructions when available. If
there is no pinned direction or configured tool process, show at least three genuinely distinct,
reference-grounded directions with visual choices and honest tradeoffs. Let the human choose.
A reference explicitly given as the direction is already a choice. Record
the chosen direction and source in the planning artifact. **Checkpoint 2:** the human locks the
direction before UI code. Never invent a tool-specific ritual or claim a tool ran when it did not.

For a CLI, library, API, agent binding, or other nonvisual deliverable, define an **interaction
contract** instead: invocation or entry point, inputs, outputs, errors, discovery, and the first
successful use. Present competing decisions only where a real choice exists. Checkpoint 2 is the
human's confirmation of any unresolved interaction choice, not an artificial visual vote.

## Phase 3 — Approval gate (greenfield)

Present the product and user, verbatim NOT list, chosen visual direction or interaction contract,
stack if applicable, absolute intended project path, and how the result will run or be exercised.
**Checkpoint 3:** ask for an explicit go/no-go on this reconciled summary. Product-root creation,
scaffolding, dependencies, and code start only after go. A prior explicit approval of this same
summary counts; a generic request to build or urgency does not. Keep planning artifacts outside
the product root until approval.

## Phase 4 — Project setup (greenfield)

After approval, establish the agreed root. If it already contains this project, inspect and
preserve it; never run `git init` over existing history or overwrite instructions or user files.
For a new root, scaffold only the agreed stack. Add appropriate ignore rules, a safe example of
required configuration, and a runnable README. Keep secrets out of tracked files.

Persist the confirmed roadmap and NOT list in `docs/ROADMAP.md`, with slices and one-line
verification steps. Keep `docs/DECISIONS.md` for decisions and reversals, `docs/PUNCHLIST.md` for
deferred findings, and `docs/HANDOFF.md` for session state. Existing equivalent records can be
extended instead of duplicated. Move the external planning facts into the project records when
safe; retain the external copy until transfer is verified.

For new projects, place portable root instructions in `AGENTS.md` and any harness binding the
project actually uses. They point to `.mario/AGENTS.md`; that file routes to `METHOD.md`, roles,
and harness-specific instructions. Configure `.mario` as an available, stable pointer to the
mario checkout and ignore it if local. Do not copy a stale snapshot of the method. Do not replace
existing instruction files without reconciling their content.

Create a git repository, remote, vault note, editor workspace, or Workforces state only when
requested or configured and useful for this project. A remote's visibility is the user's choice;
private is the default for a new remote. Report which integrations were used and any that were
unavailable. Setup approval covers routine setup steps; do not ask again for each reversible step.

## The build loop

Work one slice at a time. A slice is one behavior with a verification step a reviewer can run.
Select the lane by the consequence of being wrong and name it before building:

| Lane | Use for | Plan and review |
|---|---|---|
| Full | User-facing surfaces, auth, money, data changes, decisions, security, or hard-to-reverse behavior | Architect plan with interfaces, edge cases, files, and first-run impact; independent reviewer and meaningful checks. Include design review for visual work. |
| Short | Cheap, obvious, reversible changes such as a small fixture or local config update | A written in-thread plan with scope, files, and **Verify by** is enough; independent review still checks the diff and verification. |

Classify by consequence, never filename: auth, deployment, data, or security configuration is
full-loop when an error would be costly.

The architect plans; the implementer builds exactly the agreed slice and discloses deviations;
the reviewer reads the diff independently and runs the verification. Use a different model for
review where the harness supports it. The scribe may be delegated, but the coordinator is
responsible for the records. No role's inability to spawn another role blocks its own bounded
task. Findings outside scope go to `docs/PUNCHLIST.md` and remain untouched unless the user
expands scope.

The reviewer compares against the agreed baseline and includes committed, staged, unstaged, and
untracked changes introduced by the slice. Exclude pre-existing user work from findings, while
accounting for its effect on verification. Check correctness, security, plan compliance,
undisclosed stubs, and errors. Report a concrete consequence with each material finding. A
material issue blocks the slice; the implementer fixes it and the reviewer performs a focused
re-review. If none remain, say **clean**, with verification evidence and limits. A review does
not certify usability.

Every success claim names the actual command or interaction and its observed result. A planned
check that was not run is labeled unverified. Tests should exercise behavior and risk, not mirror
the implementation. Empty states should tell the truth and give a useful next action; use demo
data only when clearly labeled. Disclose every remaining stub in the report. Never present a
hardcoded core promise as complete.

## Phase 5 — First run

Run the deliverable in the environment and scenario from Phase 1 and exercise its primary path
with real input. A UI is opened at the relevant viewport and captured from the running build;
check discovery and affordances, primary path, scenario fit, and stubs. A CLI is invoked with
real arguments and its output and failure behavior observed. A library or API is called by a real
consumer or representative client. A binding or workflow is invoked through its actual harness
or validated with the closest executable integration check. Record exactly what the agent could
exercise and what remains unverified.

Show the human the working result and evidence, even while acceptance is pending. **Checkpoint
4:** the human decides whether the primary path is usable. Agent verification and a clean code
review are separate from this acceptance. If the user says no, fix the blocker and repeat the
relevant first run. Do not call the deliverable accepted while the verdict is pending. Include
real captures or transcripts appropriate to the medium in the build report, with stubs and limits.

## Phase 6 — Delivery target

Choose a deployment or distribution target only when this product needs one, after its runtime
needs are known. Check persistent processes, jobs, storage, platform APIs, and secrets against
the actual implementation. Document the chosen run or distribution path in the README. Do not
create a remote or publish without the user's authorization.

## Session records

Record decisions with why and when to revisit, deferred findings with status, and a brief
handoff with state, completed work, blockers, and the next action. Use in-repo records first;
optional configured external notes are secondary. A project may opt in to Notion session notes
through its ignored local configuration; follow
[the Notion session-note procedure](docs/NOTION-SESSION-NOTES.md) for authorization, receipts,
read-back verification, and duplicate-safe retries. On resume, read the records before acting.
