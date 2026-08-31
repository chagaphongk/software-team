# When PLAN doesn't fit one session

Read this when `## PLAN output shape (T1/T2)` in `references/t1.md` flags the work as oversized. Some
tasks only reveal their true size once you start drafting. Use these terms: a **fork**
(options that genuinely diverge, already sharp enough to ask) versus **fog** (a question
you can tell is coming but can't yet phrase sharply enough to act on).

**Stay inline** for the ordinary case — one or two forks, each answerable by asking the
human a direct question: draft the plan as normal, with each fork as an explicit question
in Step 3 of `## PLAN output shape`.

**Prefer a dedicated wayfinding/decision-map skill when one is installed** for work that
won't finish in one session — a fix or feature spanning sessions is exactly its shape.
Recommend the human invoke it, handing off the draft destination, the forks, and the fog
so charting doesn't start cold; its map then owns the multi-session continuity instead of
the Phase Map below. **The map replaces the Phase Map, not the office loop**: each ticket
the map marks ready to build comes back through the office as a normal task — its own
`## PLAN output shape`, tier, and BUILD → REVIEW → VERIFY cycle — and its completion is
reported back to the map, so charting and building alternate until the destination is
reached.

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

Once the human confirms the breakdown, draft `## PLAN output shape` for Phase 1 only.
Close each phase through the normal office loop and log the phase's completion as a
course-changing decision in `docs/decisions.md`.
