# Local ticket tracker

The backing store for tickets that must survive across sessions. Local files only — no
GitHub, no `gh`, no network. `references/wayfinder.md`, `references/to-spec.md`, and
`references/to-tickets.md` all write here; read this first, they build on it.

Tickets live in `.claude/state/tracker/`. That path sits inside the write carve-out
`SKILL.md` already grants the orchestrator ("you may append to `docs/decisions.md` and
`.claude/state/` directly") — creating and updating a ticket file is the same office-state
write as a decision-log line, so no builder spawn and no new carve-out language. Project
files are the opposite case: `CONTEXT.md`, `docs/adr/`, and anything else a human would
call project documentation go through a builder spawn like any other file
(`references/unsettled-requirements.md`).

## Ticket shape

One ticket, one file: `.claude/state/tracker/<id>-<slug>.md`. `<id>` is the stable
reference other tickets block on; `<slug>` is the human-readable half and can be reworded
without breaking a `blocked_by` edge.

```
---
id: <the <id> prefix of the filename — stable, never reworded>
title: <one line>
status: open|blocked|closed
type: grilling|prototype|research|task   # wayfinder tickets only — see references/wayfinder.md
blocked_by: [<id>, <id>]                 # empty list when nothing blocks it
created: YYYY-MM-DD
---
```

No index file — `ls .claude/state/tracker/` **is** the index. Exactly two things in that
directory are **not** tickets, and are excluded from the schema above and from the frontier
scan: `MAP.md` (wayfinder's decision map, `references/wayfinder.md`) and `*-spec.md`
(`references/to-spec.md` output, whose `status: ready-for-agent` is deliberately outside
the ticket enum and which carries no `id`/`blocked_by`). The `*-spec.md` suffix is a naming
hint for humans, not the authoritative signal — a ticket whose slug happens to end in
"-spec" is still a ticket; what actually excludes a file from the ticket schema and frontier
scan is its `status: ready-for-agent` frontmatter field. Everything else is a ticket.

`blocked` and an empty-but-unresolved `blocked_by` mean different things: `blocked` is a
ticket held up by something outside the tracker (waiting on a human, an external release);
a ticket waiting only on other tickets stays `open` and is simply not on the frontier yet.

## The frontier

A ticket is on the frontier when its own status is `open` and every id in `blocked_by` has
`status: closed`. Everything on the frontier is safe to build or resolve next, in any
order; everything else is waiting on something. Blocking edges across tickets form a DAG —
a cycle means two tickets each claim the other decides first, which is a fork for the
human, not a tracker state.

## Closing a ticket

Closing is a normal task completion, not a separate ceremony:

1. Flip `status:` to `closed` in the ticket file.
2. Append one line to `docs/decisions.md` per `SKILL.md`'s Continuity section, naming the
   ticket file:

```
- YYYY-MM-DD: <decision or shipped behavior> — <why> (.claude/state/tracker/<id>-<slug>.md)
```

`docs/decisions.md` stays the single decision log. Never open a second one inside the
tracker — the ticket file holds the ticket's own detail, `docs/decisions.md` holds the
chronology.
