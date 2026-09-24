---
description: Kickoff gate for a new project — intent and scope, visual direction or interaction contract, explicit approval before product code, and a real first run.
---

# /start-project

Invoke the `start-project` skill and run all six phases in order.

```
/start-project                   → full gate
/start-project [idea or roadmap] → seed Phase 1 with the given context
```

Phase 1 settles where the roadmap comes from if that is not already clear. A pasted roadmap is
**input**, not approval to build; ask only for the missing scope decisions.

**Human checkpoints:** the roadmap and NOT list (1), visual direction or unresolved interaction
choice (2), go/no-go on the reconciled summary (3), and acceptance of the real first run (4).
If a required answer is missing, wait rather than guessing.

After approval, use the slice loop in `METHOD.md`. Workforces may coordinate ongoing execution
when it is configured; it is not required.
