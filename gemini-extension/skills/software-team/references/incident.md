# INCIDENT playbook

Something is down or broken in production right now. No new persona — existing roles in
a fixed order:

1. **Triage** — `researcher`, read-only diagnosis: what broke, since when, blast
   radius, and which reversible mitigation is available. A diagnosis, not a fix.
2. **Mitigate** — human approval first (same bar as any deploy), then `deployer` runs
   a **reversible mitigation only**: rollback, restart, feature-disable. Never a new
   forward code/config fix — that becomes a normal T2 BUILD once the service has
   recovered. The diagnosis substitutes for the usual prior gates on the deployer's
   spawn.
3. **Confirm** — `verifier` confirms recovery with evidence.
4. **Postmortem** — `documenter` writes a one-page postmortem after recovery is
   verified; its operational claims trace to the researcher's diagnosis and the
   deployer's/verifier's recorded evidence (there may be no code diff to cite).

The mitigate-then-verify order is the one exception to the Done gate's usual
verify-before-deploy order — the mitigation is what the recovery verification confirms.
