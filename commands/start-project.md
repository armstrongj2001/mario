---
description: Kickoff gate for a new project — intent and scope, /impeccable for design, explicit approval before any code, and a running localhost build a person can use before the reveal.
---

# /start-project

Invoke the `start-project` skill and run all six phases in order.

```
/start-project                   → full gate
/start-project [idea or roadmap] → seed Phase 1 with the given context
```

A pasted roadmap is **input to Phase 1**, never a substitute for it and never approval to build.
The Phase 3 gate cannot be waived, and Phase 5 — running it on localhost and using it — cannot be
skipped because the reviews passed.

Hands off to `@architect` on approval, and to `/work` for ongoing execution.
