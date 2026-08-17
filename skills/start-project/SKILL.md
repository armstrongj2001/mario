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

## Phase 1 — Intent

Write nothing yet. Not a folder, not a `package.json`, not a "quick prototype".
A pasted roadmap is **input**, not approval — roadmaps list features, never who it is for or
what it must not become.

Say: *"Running kickoff gate — four questions before any code."* Then ask, in one batch:

1. **What is it?** One sentence a stranger would understand.
2. **Who opens it, and what do they do in the first 30 seconds?**
3. **What does it explicitly NOT do?** ← the scope boundary. Force a real answer.
4. **Success looks like…?** A screenshot, signups, a demo?

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
direction `init` landed on, and the stack.

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
