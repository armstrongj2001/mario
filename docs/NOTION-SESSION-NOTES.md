# Optional Notion session notes

Mario can publish a short session note to an existing Notion page or database after the
in-repo records are current. This is an optional secondary record. It requires a Notion app or
MCP connector that is already installed, connected, and available to the coordinating agent.
Mario does not install a connector, store credentials, or create a database schema.

## Opt in for a project

Create `docs/session-notes.local.md` under the active project root and add
`/docs/session-notes.local.md` to that project's `.gitignore`. Keep the file local because it
may identify a private workspace. Use this template:

```markdown
# Session notes

enabled: true
destination: <page or database URL/ID>
destination_kind: page|database
project: <name>
```

These lines are instructions for the agent, not input to an executable parser. The agent reads
them in context and resolves the file from the active project, even when Mario itself is linked
from another checkout. Do not put credentials in the file.

The user's opt-in is authoritative:

- When the file is missing or `enabled` is not `true`, do not publish automatically. A user's
  explicit request for this session may authorize a one-off note. For a one-off, record the
  supplied destination, project, and receipt in the ignored local file before the external call;
  the current request supplies the enablement.
- A destination must be present and its kind must be `page` or `database`.
- A URL found in an old handoff, decision, or session note is historical context, not permission
  to publish again.
- A configured vault or session-note skill may be used alongside Notion. Notion does not replace
  it or the repository records.

## Closeout procedure

1. Update the project's `docs/DECISIONS.md`, `docs/PUNCHLIST.md`, and `docs/HANDOFF.md` as
   applicable. Local closeout is complete even when external publishing is blocked.
2. Read the local opt-in and confirm that the named destination, authorization, and connected
   Notion tools are available. If any are absent, report the external blocker without installing
   software, requesting broader access, or weakening the local closeout.
3. Allocate one stable `session_key` before any create call. Use the configured project name and
   the session's UTC start, for example `mario-20260925T163000Z`. Reuse that exact key for every
   attempt for the session.
4. Fetch the destination before writing and follow the applicable installed Notion skill and
   live connector schema. For a page destination, create a child page. For a database, create an
   entry using its actual title property and any required fields. Use only properties that
   already exist; do not add or alter a schema to fit the note.
5. Write a short note containing the current state, durable decisions, user corrections,
   verification evidence, open work, the single best next action, and useful repository links.
   Include the exact `session_key`. Exclude credentials, machine-specific paths, unrelated
   session content, and a narrative replay of the diff.
6. Record the result locally as described below. A returned page ID is persisted immediately,
   before any follow-up call. Fetch the result and confirm its parent, exact `session_key`, and
   substantive note content before marking it `published`.

The coordinator owns connector calls when the scribe cannot make them. The standard Claude
scribe keeps its `Read`, `Grep`, and `Write` tools; publishing does not require expanding that
role's permissions.

## Receipts and retries

Append a receipt under `## Receipts` in `docs/session-notes.local.md` for each session key:

```markdown
### <session_key>
- status: pending|published|failed|uncertain
- page_id: <returned ID when known>
- url: <returned URL when known>
- last_attempt: <UTC timestamp>
- detail: <short result, verification, or blocker>
```

Create the `pending` receipt before the first external write. Update that receipt in place after
each attempt; do not create a second receipt for the same key.

Keep destination IDs, page IDs, and page URLs in this ignored receipt. A tracked repository
handoff records only the external-note status or blocker. The user-facing closeout message may
include a verified page link.

- If `page_id` is known, fetch that page first, verify the key and destination, and reuse it.
  Update only the smallest necessary content.
- If a create call has an uncertain outcome and no ID was returned, enumerate or search within
  the same destination for the exact `session_key` before retrying.
- If exactly one matching page is verified, persist its ID and reuse it. If there are multiple
  matches, the destination cannot be enumerated, or the match cannot be verified, leave the
  receipt `uncertain`, report the blocker, and do not create another page.
- Use `failed` for a definite rejected write or unavailable required capability, with the reason
  in `detail`. Use `published` only after the read-back checks succeed.

## Expected outcomes

| Situation | Result |
|---|---|
| File absent or disabled | Finish local closeout; no automatic Notion call. |
| Enabled; write and read-back succeed | Persist the returned ID, read back parent, key, and content, then mark `published`. |
| Connector or authorization unavailable | Finish local closeout; mark the receipt `failed` and report the blocker. |
| Destination is missing or its database schema cannot support the note | Do not write or change schema; mark the receipt `failed` and report the blocker. |
| Known page ID after an interrupted attempt | Fetch, verify, and minimally update that page. |
| Uncertain create with one exact match | Reuse the match after persisting its ID. |
| Uncertain create with multiple or unverifiable matches | Mark `uncertain` and defer; do not risk a duplicate. |
