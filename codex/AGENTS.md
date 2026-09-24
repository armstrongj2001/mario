# Codex binding

Read `METHOD.md` and `roles/*.md` at the mario root first. Resolve that root from the
project's `.mario/` symlink, or the current checkout when it contains this binding,
`METHOD.md`, and `roles/`. If neither exists, request the mario checkout path; do not
invent role instructions. This file supplies routing, not a second method.

## Model routing

| Role | Model | Reasoning | Default sandbox |
|---|---|---|---|
| architect | `gpt-6-astra` | high | read-only |
| implementer | `gpt-5.6-sol` | high | workspace-write |
| code-reviewer | `gpt-5.6-terra` | high | workspace-write |
| mario-scribe | `gpt-5.6-luna` | medium | workspace-write |

Use native subagents for delegated roles when available. For a full-loop slice, hand
off architect → implementer → code-reviewer. A cheap reversible slice may use a
written in-thread plan, but still gets independent review. Delegate the scribe when
useful; the coordinator remains responsible for records. Pass the agreed scope,
NOT list, files, baseline including pre-existing changes, exact Verify by step, and
artifact inputs at each bounded handoff. Dependent steps run in order. Only
independent work runs in parallel, with one writer per file. The coordinator may
implement an approved plan if already using Sol; review still belongs to fresh
Terra.

Prefer the installed named agents from `codex/agents/*.toml`. If the harness exposes
explicit model selection but no named-role selector, pass the model and reasoning
from this table in the actual spawn call, together with the absolute role-file path,
the approved plan, and the bounded task. A role name in a prompt does not select a model.
On harnesses with `fork_turns`, use `none` or a bounded fork when required for model
overrides; provide the needed context explicitly. Reviewers receive the plan and diff,
not the implementer's conversational rationale.

Check the available models before dispatch. If a configured model fails from
capacity or availability, retry that dispatch at most once. Then report the failed
handoff and request or use an explicitly authorized replacement; never silently
inherit the parent model or report that the configured chain ran. If native subagents or model
selection are unavailable, disclose that limitation and use the sequential fallback
in the root AGENTS.md without claiming independent or different-model review.

For unresolved material findings or high-risk concerns, an explicit fresh Astra
review may supplement Terra. It never replaces Terra or waives its findings.
Dispatch that escalation separately with an explicit Astra model and the reviewer
role path; do not invoke the named Terra TOML with a conflicting model override.
Return fixes to Sol and give Terra a focused re-review.

For each handoff, announce the role and requested model. Record the returned agent
identifier, result, and verification command/output. Distinguish the configured or
requested model from runtime-confirmed metadata. An agent claiming its own model
identity is not verification of backend routing.

## Enforcement limits

The TOML files configure spawned sessions; merely storing them here does not install
them. Follow README.md to install them, explicitly register them with
`scripts/register_codex.py` when required by the client, and start a fresh session.
The tested CLI 0.155.1 exposed the role metadata after `[agents.<name>]` registration
in user configuration, but a fresh named dispatch still failed with `agent type is
currently not available`. Registration is not proof of runtime dispatch; follow the
explicit-model fallback above when the available spawn tool supports it. These files
do not launch agents on their own: the coordinator must perform the handoffs above.

Architect read-only is a sandbox default, not Claude's tool allowlist. Parent runtime
permission overrides, including bypass mode, can override it. If the spawn interface
does not expose per-role permissions, announce that the no-write rule is instructional.
Reviewer uses workspace-write to allow test caches and build artifacts; its prohibition
on editing product code is instructional. Scribe's record-only scope is instructional too.
Never claim these writable roles are physically unable to edit code.

For downstream projects, their root AGENTS.md must point to `.mario/AGENTS.md` (or
explicitly to this file as well as the method and roles). A pointer only to METHOD.md
and roles does not load this routing binding.
