# Debugging before PLAN

Read this before drafting anything for a bug report, a failing test, or behavior nobody
can explain — a bug report names a symptom, not a cause.

Spawn `software-team:researcher` with these steps as its `Task:` (it holds `Bash` for
exactly this: running a repro script, existing tests, or requests against a running
instance is investigation, not building — see its contract). Do the steps yourself only
for a repro so trivial there's nothing to delegate. Don't let PLAN start until step 3 has
actually happened, not just been assumed:

1. **Reproduce** — get a reliable repro first: the exact input/command/request that
   triggers it, confirmed to actually fail. A fix for a bug you haven't reproduced is a
   guess wearing a diff. **If the failure is intermittent or timing-dependent** (a race,
   a flake, "sometimes"), a single pass/fail proves nothing — state a hit rate over N
   repeated attempts (e.g. "12/50 failed with a 50ms stagger between two concurrent
   requests"), varying the relevant parameter (delay, concurrency, load) across the runs
   instead of repeating one identical case.
2. **Trace** — follow the real failure path: the actual stack trace or error output, not
   an assumed one; read the code the trace actually passes through, not the code you'd
   expect it to pass through. For a concurrency bug, trace specifically for where an
   "already happened" guard exists (or should) and whether it sits before or after the
   operation it's meant to guard.
3. **Hypothesize, then falsify** — form one concrete hypothesis for the root cause, then
   try to prove it wrong before believing it. Pick the falsification method the bug
   shape actually allows: a targeted log line or a minimal isolating test for a
   deterministic bug; **for a race or timing bug, use logging plus repeated automated
   runs, never a debugger break** — pausing execution changes the timing window you're
   trying to observe, so it can hide the very race you're testing for. A hypothesis that
   survives an honest attempt to break it is worth building a fix on.
4. **Cross-reference** — check whether the same root cause reaches other callers or
   paths: grep for the pattern elsewhere, check `git blame`/history for when it was
   introduced, check for related past fixes. A fix scoped only to the reported symptom
   leaves siblings broken.

Once the root cause is confirmed — not assumed — this becomes a normal PLAN per
`## PLAN output shape` in `SKILL.md`, with one addition to the acceptance criteria: a
regression test that reproduces the original failure and fails without the fix. **For a
bug that's inherently flaky**, a single deterministic assert isn't achievable — the
acceptance criterion instead states the hit rate the fix must drive to zero (or
near-zero) over a stated N runs, or verifies the structural guard directly (e.g. a DB
unique constraint or an idempotency check the verifier can confirm statically), rather
than chasing a test that "always" passes for a bug that never always failed. BUILD for
this PLAN spawns `software-team:tdd-builder`, not the general builder — the regression
test IS its first red step, written and confirmed failing before the fix, not added
after.
