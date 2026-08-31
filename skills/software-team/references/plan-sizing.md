# When PLAN doesn't fit one session

Read this when `## PLAN output shape (T1/T2)` in `references/t1.md` flags the work as oversized: you
can't state a **Destination** in one or two lines without hedging, drafting Step 3 turns
up more than two or three genuine forks, or a fork's own resolution needs investigation
spanning more than this session.

Some tasks only reveal their true size once you start drafting: the "one clear ask" from
Step 1 turns out to hide several genuinely diverging forks, or an acceptance criterion
can't be written because an earlier step first needs its own investigation. Use these
terms for the two things that can be wrong with a plan's size: a **fork** (options that
genuinely diverge, not yet decided — already sharp enough to put to the human) versus
**fog** (a question you can tell is coming but can't yet phrase sharply enough to act on
at all — coarser than a fork, not yet ready to ask).

**Stay inline** for the ordinary case — one or two forks, each answerable by asking the
human a direct question, nothing that needs its own multi-session investigation: draft
the plan as normal, with each fork as an explicit question in Step 3 of `## PLAN output
shape`. Most T1/T2 tasks never leave this path.

**Prefer `wayfinder` when it is installed** for work that won't finish in one session — a
fix or feature spanning sessions is exactly its shape. Recommend the human invoke
`/wayfinder`, handing off the draft destination, the forks, and the fog so charting
doesn't start cold; its decision-ticket map then owns the multi-session continuity
instead of the Phase Map below. **The map replaces the Phase Map, not the office loop**:
each ticket the map marks ready to build comes back through the office as a normal task —
its own `## PLAN output shape`, tier, and BUILD → REVIEW → VERIFY cycle — and its
completion is reported back to the map, so charting and building alternate until the
destination is reached.

**Break into phases** when the sizing signals hold and no wayfinding skill is installed —
don't force a plan that's likely to break on contact with the work just to have something
to present. Draft a **Phase Map** instead of a single PLAN, and present it for approval
before drafting Phase 1's actual plan:

```
This is bigger than one plan — [N] forks, and [what's still too foggy to phase yet].
Proposed phase breakdown instead of a plan likely to break on contact:

Destination (draft): <best one-line attempt, marked as a draft — may sharpen as phases close>
Phase 1: <name> — <what it covers, sized to fit one PLAN -> BUILD -> REVIEW -> VERIFY cycle>
Phase 2: <name> — <...>
Forks that decide phase order/scope: <list, one line each — put to the human, not answered for them>
Fog: <what's clearly coming but not sharp enough to phase yet>

Confirm the phase breakdown (and the forks above), or tell me to adjust it — Phase 1 gets
its own PLAN once this is approved.
```

Never silently draft a monolithic plan for work you've just told the human is too big for
one — that's the exact failure this file exists to catch. Once the human confirms the
breakdown, draft `## PLAN output shape` for Phase 1 only. Close each phase through the
normal office loop (RESEARCH → PLAN → BUILD → REVIEW → VERIFY → DONE) exactly as for any
other task, and log the phase's completion as a course-changing decision in
`docs/decisions.md` — reuse that existing continuity mechanism rather than a new
artifact. Re-check the sizing signals before drafting each later phase's PLAN: a phase
can itself turn out oversized once its own detail becomes visible, and fog can graduate
into new phases the original breakdown didn't foresee — update the Phase Map and
re-confirm with the human when that happens, rather than quietly absorbing the change into
whichever phase is in progress.
