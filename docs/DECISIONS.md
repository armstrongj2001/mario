# Decisions

## 2026-09-21 — Codex role routing

- Chose: separate Codex bindings referencing the shared method and role files; Terra plans/reviews,
  Astra implements, Luna records decisions. Explicit spawn parameters support harnesses without
  named-agent selection.
- Over: relying on Claude frontmatter or inherited parent models in Codex.
- Because: role prose does not select a runtime model. Named TOML bindings and explicit dispatch
  make the requested routing inspectable while preserving one shared method.
- Revisit if: model availability changes or Codex exposes stronger per-role tool restrictions.
- Limits: templates need installation for named discovery; runtime permission overrides can
  supersede sandbox defaults; a child self-report is not backend model evidence.

## 2026-09-21 — Sol implements; Claude remains intact

- Chose: GPT-5.6 Sol for the Codex implementer, superseding the Astra assignment above.
- Over: omitting Sol from the coding role.
- Because: the user wants Codex added alongside the existing Claude architecture and called out
  Sol's absence. Claude's bindings and model assignments remain unchanged.
- Revisit if: the user requests another model or Sol is unavailable.

## 2026-09-21 — Keep Astra in the role chain

- Chose: Astra architect, Sol implementer, Terra reviewer, Luna scribe. This supersedes the
  Terra architect assignment; Sol remains implementer.
- Over: removing Astra when adding Sol.
- Because: the user explicitly wants Astra retained. Assign it architecture and planning while
  Sol implements and a separate Terra agent reviews. Claude remains unchanged.
- Revisit if: the user changes the assignments or a configured model is unavailable.

## 2026-09-21 — Quality-first workflow overhaul

- Chose: retain the existing role architecture and both harnesses; fix contradictory rules,
  portable setup, bounded handoffs, independent review evidence, and reproducible installation.
- Over: adding more permanent agents or optimizing primarily for token cost.
- Because: the user clarified “i meant to say the best it possibly can.” The initial
  interpretation of “out of pocket” as a cost constraint was incorrect.
- Revisit if: observed workflow failures require a specialized role rather than a clearer
  contract or better verification. Do not add agents merely to make the chain longer.

## 2026-09-21 — Quality semantics

- Chose: preserve the human checkpoints and NOT list while making greenfield, maintenance, and
  resume routes explicit; require a nonvisual interaction contract where visual direction does not
  apply; treat first-run evidence and human usability as separate from review cleanliness.
- Over: collapsing all work into the greenfield gate or treating passing static checks as acceptance.
- Because: the overhaul must improve output quality without losing scope control, actual-use
  evidence, or the user's explicit product boundary.
- Revisit if: a later harness supplies stronger equivalent checkpoints with durable evidence.

## 2026-09-21 — Safe coexistence and diagnostics

- Chose: install Claude and Codex bindings side by side, preserve existing user files and optional
  integrations, make repeat installation idempotent, and keep doctor source/installed/project
  checks read-only with truthful missing-state results.
- Over: replacing user configuration, deleting foreign Workforces, or reporting live routing from
  static configuration alone.
- Because: installation is a reversible setup operation and must not damage unrelated harness
  state; diagnostics must distinguish configured intent from runtime proof.
- Revisit if: a supported host changes its discovery or ownership rules.

## 2026-09-21 — Setup review closes

- Chose: validate required routing documents as well as agent definitions; preserve executable
  installer behavior; use identical default-home rules in installer and diagnostic.
- Over: treating parsed role TOMLs and passing happy-path installation as sufficient evidence.
- Because: independent review and regression checks exposed missing entry-point coverage, a
  file-mode regression, and empty environment values resolving to different paths.
- Revisit if: the harness changes discovery format or installation locations. Static checks
  still do not certify named-agent runtime dispatch or a human usability verdict.

## 2026-09-24 — One repository and an explicit Codex registry

- Chose: finish on `upgrade/claude-codex-workflow`, then fast-forward and push existing
  `main`; preserve the seven earlier local commits. No separate Codex repository.
- Because: the user wants the existing repo updated with Claude and Codex side by side.
- Runtime evidence: CLI 0.155.1 did not discover named roles from installed TOML links
  alone. Explicit registration exposed role metadata, but persistent named dispatch still
  failed. An earlier subprocess reported success without a raw spawn event; that is
  insufficient evidence to certify reliable named dispatch.
- Chose: a separate opt-in `scripts/register_codex.py` helper, rather than silently
  editing global config from the symlink installer. It preserves unrelated bytes,
  rejects conflicting roles, backs up existing config, and rechecks before replacement.
- Limit: unrelated concurrent writers cannot be locked out; close config editors during
  registration. This residual check-to-replace race is documented.
- Revisit if: Codex changes its discovery mechanism. Keep configured model identity,
  runtime-exposed metadata, and backend attestation distinct.

## 2026-09-25 — Claude bindings pinned to current models; Fable opt-in

- Chose: pinned IDs — architect and implementer `claude-opus-5-5`, reviewer
  `claude-sonnet-5`, scribe `claude-haiku-4-5`. `claude-fable-5-1` is an opt-in architect
  variant, asked on first interactive install and switched with `--fable` / `--no-fable`.
- Over: floating aliases; Fable by default.
- Because: the user wants the bindings to name the current models, and Fable's price keeps
  most users off it. The variant sits outside `agents/` so plugin discovery sees one architect.
- Revisit if: a model is superseded or Fable pricing drops toward Opus.
