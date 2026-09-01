# Wayfinder — charting work too big to plan in one go

`references/plan-sizing.md` escalates here when a Phase Map isn't enough: fog that keeps
recurring after drafting, a fork whose resolution needs its own multi-session
investigation, or work spanning independent sessions or contributors. This is the office's
own path — nothing external to install. Tickets and the map live in the local tracker
(`references/tracker.md`).

**Wayfinder plans, it does not build.** `SKILL.md` Hard rule 7 — "Deciding is not building"
— binds every ticket here: resolving a `grilling` or `research` ticket produces a recorded
decision, never production code. A map that carries execution license is the documented
failure mode this file exists to prevent — the moment a ticket starts sounding like an
implementation, it belongs in `references/to-tickets.md`, not on the map.

## The map

Draft the map **before any ticket exists**, at `.gemini/state/tracker/MAP.md` — the one
file in the tracker directory that isn't a per-decision ticket. Present it to the human
before charting further.

```
# Map: <name>

Destination: <one line — what success looks like>

Decisions so far:
- <decision> (.gemini/state/tracker/<id>-<slug>.md)

Fog of war:
- <anticipated decision, not yet sharp enough to phrase as a ticket>

Out of scope:
- <what this map will not reach>
```

**Decisions so far** grows as tickets close, each linked by its file path.
**Fog of war** carries `references/plan-sizing.md`'s existing sense of the word — a question
you can tell is coming but can't yet phrase sharply enough to act on, coarser than a fork.
A fork is already sharp enough to put to the human; fog is not, so fog never becomes a
ticket directly — it graduates into one once it sharpens.

## Ticket types

Every map ticket carries a `type:` in its frontmatter (`references/tracker.md`):

| `type` | Loop | Resolved by |
|---|---|---|
| `grilling` | HITL | Conversation with the human until the question settles |
| `prototype` | HITL | A built throwaway artifact that answers a question prose can't |
| `research` | AFK | Spawn `researcher` against the ticket — facts external to the working directory |
| `task` | — | Manual work that unblocks other decisions; **never** implementation of the feature itself |

A `prototype` ticket's artifact is evidence for a decision, not the start of the build —
it is thrown away and the real work goes through the normal office loop later.

## Working the map

Take one ticket per session from the frontier, or present the frontier list and let the
human pick. A ticket is on the frontier when its own status is `open` and every id in
`blocked_by` has `status: closed`. Resolve it, close it per `references/tracker.md`, then
move its decision into the map's **Decisions so far** and re-read **Fog of war** — a closed
decision usually sharpens one fog item into the next ticket.

## When the map closes

The map is closed when the destination is reachable from the decisions recorded and the fog
is either cleared or explicitly accepted as residual. Hand off to `references/to-spec.md` to
synthesize the closed map into a spec — **never straight to PLAN or BUILD**. The map is a
record of what was decided, not a licence to execute; the spec is what a fresh session
builds against.
