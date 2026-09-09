# EXP-498: bring the extra-return boundary to the primitive-cycle point

The next numerical test is implemented and its preflight controls pass.
No new target result is claimed in this checkpoint.

[EXP-497](2026-09-09-exp497-contact-localization.md) supplied a primitive-cycle
point close to one measured right-hand fold. The earlier grazing/extra-turn
evidence was obtained at different parameters. EXP-498 recomputes that boundary
at the exact new cycle parameters, rather than transporting a C/D label by
assumption.

## What will run

- All eight first-case boundary nominations, including the old failed
  depth-eight/direction-zero/candidate-one accuracy comparison.
- Both DOP853 and Radau; unchanged root, event, paired-state and winding gates.
- Four fixed opposite-side displacements per qualified paired root.
- The complete 26-parent ledger, with eighteen unrun rows and explicit reasons.
- All six cycle events in both repeat windows when comparing the last regular
  return before grazing. The grazing state itself is not that preceding input.

New root boxes are declared prospectively around the old fitted roots, at the
new parameter value. Old boxes, outcomes and failures stay unchanged. A new
success does not retroactively repair the old failed comparison. The maximum
is 192 retained target integrations, plus the separately bounded tiny guards.

The test can establish a local boundary mechanism at the same parameters as
the cycle, and describe its input geometry. It cannot certify a second smooth
critical point, invariant quotient, C/D, a Jones word or an insertion arrow.
All eight new boundary/turn matrices must qualify before the overall input
ordering receives a positive label; no subset can rescue that conclusion.

## Preflight evidence

The 18 focused tests pass. They cover deterministic selection and seeds,
section transport, old-failure retention, frozen constants, predecessor versus
grazing identity, complete all-index distances, independent scalar arithmetic,
missing-arm handling, and the signed-ray winding replay.

All five actual analytic boundary controls and twelve exact-data polygon
controls pass in `artifacts/EXP-498/preflight-controls-01/controls.json`.
The control receipt has SHA-256
`d8841de84fd805e9ae0dde400528aece9712e685c53d4a69caa4e2af9d422bac`.
Its saved decisions and exact-polygon controls also replay with numerical
integrators explicitly forbidden. The complete import closure has 83 paths
and no missing imported project module. The public auditor CLI starts
successfully. The full suite passes **2,216 tests**, with one existing
Linux-only skip and no failures, in 141.74 seconds; the receipt is
`artifacts/EXP-498/preflight-tests-01.xml`.

- [Prospective protocol](../experiments/EXP-498-boundary-transport.md)
- [Machine plan](../../experiments/manifests/EXP-498-boundary-transport.json)
- [Runner](../../scripts/run_exp498_boundary_transport.py)
- [Raw-data auditor](../../scripts/audit_exp498_boundary_transport.py)

The stale heartbeat was updated through the app's automation tool. It remains
active on its unchanged schedule, now reads the newest repository records,
and explicitly rejects automatic paid Pro reviews. The superseded EXP-482
instructions will not authorize repeating a completed run. No API generation,
GPU rental or restricted data upload was used.

The raw-publication approval boundaries from EXP-481/496 remain in force;
there is no alternate upload route. They do not prevent this local experiment.
