---
name: start-project
description: Mandatory kickoff gate for any new project, app, site, or major greenfield feature. Establishes intent and scope, hands design context to /impeccable init, and requires explicit approval before any code. Use when starting a new project, scaffolding a repo, building a new site or app, or when the user says start a project, new project, build me a, or pastes a roadmap.
---

# start-project — Kickoff Gate

Greenfield work fails two ways: building the wrong product, and building the right product ugly.
Both come from writing code before the target is defined.

Three phases. **No scaffolding, no dependencies, no components until Phase 3 is signed off.**

Design is not handled here — `/impeccable` owns that end to end. This skill owns *intent*,
*scope*, and the *gate*.

---

## Running the gate

These hold for every phase, without being asked:

- **Create nothing before Phase 3 approval.** No directory, no `package.json`, no `git init`, no
  "quick scaffold to hold things." If you are about to write, stop and say so instead. This is not
  waivable by `--auto`, by urgency, or by the user seeming impatient.
- **Announce each phase as you enter it**, and announce every agent handoff (`@architect`,
  `@implementer`, …) as it happens, so the chain is visible while it runs.
- **Answer from the prompt before asking.** A good brief already contains most of Phase 1 — extract
  what is there, reflect it back for confirmation, and ask only about what is genuinely missing.
  Re-asking what the user already told you is the fastest way to make this feel like a form.
- **Never skip Phase 2.** Design context is not optional, and not something to substitute your own
  taste for.
- **Do not reproduce copyrighted material.** Reference the structure and pacing of existing
  products; write original content.

---

## Phase 1 — Intent

Write nothing yet. A pasted brief or roadmap is **input**, not approval — briefs describe features
and feel, rarely who it is for or what it must not become.

Extract from what the user already gave you, then confirm and fill gaps. The four things you need:

1. **What is it?** One sentence a stranger would understand.
2. **Who opens it, and what do they do in the first 30 seconds?**
3. **What does it explicitly NOT do?** ← the scope boundary. Force a real answer.
4. **Success looks like…?** A screenshot, signups, a demo?

Ask only for what the brief did not already answer. **Q3 is almost never in a brief** — people
describe what they want, not what they are refusing. Expect to ask it, and expect the first answer
to be vague. Push once with a concrete wrong-direction guess.

Q3 is the one that prevents building the wrong thing. If the answer is vague, ask again with a
concrete wrong-direction guess: *"So it is not just a feed of your GitHub repos?"*

Record the **NOT list** verbatim. Every later scope question is settled against it.

---

## Phase 2 — Design Context

Run **`/impeccable init`**.

It asks whether the surface is brand (marketing, landing, portfolio) or product (app UI,
dashboard, tool), then writes `PRODUCT.md` and `DESIGN.md` — audience, voice, anti-references,
color, type, components. Every later `/impeccable` command reads them.

Feed it the Phase 1 answers, especially the NOT list, so its anti-references match.

Do not substitute your own taste for this step, and do not skip it because the project is
"internal" or "just a tool". If the user supplies reference sites they admire, pass them through —
`init` turns references into tokens far better than prose does.

Do not run workforces' `/brand-context`; it is superseded and would produce a competing brand file.

---

## Phase 3 — Approval Gate

Present a compact summary: what it is, who it is for, **what it will not do**, the design
direction `init` landed on, the stack, and the **deploy target**.

### Deploy target

Decide this *now*, not after the code exists. Where it runs constrains what can be built, so a
target chosen late invalidates the plan. Ask if it was not stated.

| Target | Runtime | Choose when |
|---|---|---|
| **Vercel** | Node + Edge, serverless | Frontend-led, SSR/SPA, small API routes. Default for most web work |
| **Cloudflare** | V8 isolates, edge only | Global reach, cost at scale, fastest cold start. **Not full Node** — verify every dependency runs on workerd |
| **Railway** | Containers, persistent | Long-running processes, websockets, cron, background jobs, a database you control |
| **Static host** | None | No server logic at all |

Disqualifiers to check before committing to serverless: a persistent connection, a job that
outlives a request, a scheduled task, or a dependency needing native Node APIs. Any of those
means Railway (or another container host), not Vercel or Cloudflare.

Name the storage layer too — it is part of the target, not a later detail.

Ask for explicit go/no-go.

**Code begins only after the user says go.** This gate cannot be waived — not by `--auto`, not by
"just start", not by a pasted roadmap.

---

## After the Gate

```
@architect                    plan — files, signatures, edge cases, checkpoint test
@implementer                  build the plan exactly
/impeccable audit <surface>   deterministic rules — a11y, contrast, responsive
/impeccable critique <surface> hierarchy, clarity, resonance
@code-reviewer                correctness, security, duplication
@scribe                       persist decisions and corrections
```

Run `/impeccable audit` **before** showing the user a surface, not after they complain.
Never ship an empty or placeholder state — `/impeccable onboard` handles first-run and empty states.

---

## Failure Modes

| Symptom | Missed phase |
|---|---|
| "This isn't what I asked for" | 1 — no NOT list |
| "It looks generic / AI-generated" | 2 — skipped `init`, designed from imagination |
| Design fixes arriving as the last commits | After — audit ran as cleanup instead of before reveal |
| Built the wrong thing fast | 3 — no go/no-go |
