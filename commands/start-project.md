---
description: Kickoff gate for a new project — intent and scope, /impeccable for design, explicit approval before any code, and a running localhost build a person can use before the reveal.
---

# /start-project

Invoke the `start-project` skill and run all six phases in order.

```
/start-project                   → full gate
/start-project [idea or roadmap] → seed Phase 1 with the given context
```

Phase 1 asks first where the roadmap comes from — you have one, or you build it together. A pasted
roadmap is **input**, never a substitute for the questions and never approval to build.

**Four checkpoints stop and wait for you:** the roadmap and NOT list (1), the visual direction (2),
go/no-go (3), and whether the running build is usable (4). There is no unattended mode. If nobody
answers, the run stops rather than guessing.

Hands off to `@architect` on approval, and to `/work` for ongoing execution — Phase 4 installs
Workforces in every project, so `workstate.md` and `docs/ROADMAP.md` exist for it to read.
