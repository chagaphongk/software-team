# Debugging before PLAN

Read this before drafting anything for a bug report, a failing test, or behavior nobody
can explain — a bug report names a symptom, not a cause.

Spawn the `researcher` role with these steps as its task. Do the steps yourself only for
a repro so trivial there's nothing to delegate.

1. **Reproduce** — get a reliable repro first: the exact input/command/request that
   triggers it, confirmed to actually fail. **If the failure is intermittent or
   timing-dependent**, a single pass/fail proves nothing — state a hit rate over N
   repeated attempts, varying the relevant parameter across the runs.
2. **Trace** — follow the real failure path: the actual stack trace or error output, not
   an assumed one. For a concurrency bug, trace specifically for where an "already
   happened" guard exists (or should) and whether it sits before or after the operation
   it's meant to guard.
3. **Hypothesize, then falsify** — form one concrete hypothesis for the root cause, then
   try to prove it wrong before believing it. For a race or timing bug, use logging plus
   repeated automated runs, never a debugger break — pausing execution changes the timing
   window you're trying to observe.
4. **Cross-reference** — check whether the same root cause reaches other callers or
   paths: grep for the pattern elsewhere, check `git blame`/history, check for related
   past fixes.

Once the root cause is confirmed — not assumed — this becomes a normal PLAN per
`## PLAN output shape (T1/T2)` in `references/t1.md`, with one addition to the
acceptance criteria: a
regression test that reproduces the original failure and fails without the fix. This is
also the point where the risk tier gets classified (SKILL.md Step 2): a bug whose
confirmed cause clears every T0.5 bar takes the T0.5 small path in `references/t1.md`
instead of being forced to T1. **For a
bug that's inherently flaky**, a single deterministic assert isn't achievable — the
acceptance criterion instead states the hit rate the fix must drive to zero (or
near-zero) over a stated N runs, or verifies the structural guard directly (e.g. a DB
unique constraint or an idempotency check the verifier can confirm statically), rather
than chasing a test that "always" passes for a bug that never always failed. BUILD for
this PLAN spawns the `builder` role with `Mode: TDD` — the regression test IS
its first red step, written and confirmed failing before the fix.
