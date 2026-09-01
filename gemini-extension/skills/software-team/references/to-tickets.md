# Slicing a spec into tickets

Read this when `references/to-spec.md` has produced a spec too large for one BUILD. The
output is a set of tickets in the local tracker (`references/tracker.md`), each of which
re-enters the normal office loop on its own.

## Slice vertically

A ticket is a **tracer bullet**: a thin but complete path through every layer the feature
touches — schema, API, UI, and tests together for one user-visible behavior —
independently demoable and independently verifiable.

**Never slice horizontally.** One ticket for "all schema changes", another for "all API
changes", another for "all UI changes" is the failure this rule exists to prevent: a
horizontal slice can't be tested when it lands, because the layers it needs to prove
anything haven't shipped yet, so its acceptance criteria degrade into "the code exists". A
vertical slice owns every layer it is graded on, so its criteria stay testable statements
and its verifier can actually run them.

Size each slice to fit one PLAN → BUILD → VERIFY cycle. A slice that needs its own phase
breakdown is still a spec, not a ticket.

## Ticket shape

`.gemini/state/tracker/<id>-<slug>.md`, frontmatter per `references/tracker.md`
(`id`/`title`/`status`/`blocked_by`; `type:` is wayfinder's field and is omitted here):

```
Acceptance criteria:
1. <testable statement>

Out of scope: <files/behaviors that must not change>
```

Write the acceptance criteria in the same shape `## PLAN output shape (T1/T2)`
(`references/t1.md`) uses, so a ticket hands almost verbatim into a plan. Inherit the
spec's **Seams** into the plan for whichever tickets touch them.

## Order and execution

Blocking edges across tickets form a DAG. A ticket is on the frontier when its own status
is `open` and every id in `blocked_by` has `status: closed` — that set is what's buildable
next.

Each ticket runs the normal office loop as its own task: classify the tier, draft
`## PLAN output shape (T1/T2)`, then BUILD → VERIFY → DONE per `references/t1.md`. Because
the acceptance criteria are already settled, that PLAN is usually all ratifications —
present it and proceed, don't re-derive what the spec decided. On completion, close the
ticket and log its `docs/decisions.md` line per `references/tracker.md`.

## Wide or mechanical refactors

Sequence expand-contract, one ticket per step, so CI stays green between them:

1. One ticket adds the new form alongside the old.
2. One or more tickets migrate call sites in batches.
3. One ticket removes the old form.

Each is a separate node in the DAG, blocked on the previous. Order prefactoring tickets —
the ones that reshape existing code to make the new work fit — ahead of the tickets that
depend on that shape.
