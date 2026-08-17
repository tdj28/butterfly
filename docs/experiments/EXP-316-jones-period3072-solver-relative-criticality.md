# EXP-316 — Solver-relative eighth-birth criticality

Status: failed one identity gate; subcritical classification agrees

EXP-315 shows that DOP853 and Radau place the period-1536 real-`-1` event in
disjoint numerical intervals separated by about `1.5e-13`. EXP-316 therefore
abandons the shared absolute coordinate that left EXP-310 neutral.

For each solver independently, correct the period-1536 parent and the
multiplier-blind EXP-309 negative-sign primitive period-3072 child exactly
`5e-13` above that solver's upper event bound. The targets are
`0.2407010082249473` for DOP853 and `0.24070100822464888` for Radau.

The preregistered prediction is parent stable and child unstable under both
solvers: a local subcritical eighth birth. The `1e-4` classification margin,
cross-solver node and multiplier agreement, `2e-6` child half-period
nonclosure, exact `3584/4096` section identities, and all sparse correction
gates remain. Direct closure and neutral-mode checks are explicitly bounded by
`0.01` for every corrected family.

A pass resolves only the local birth direction in event-relative numerical
coordinates. It does not prove sign equivalence, attraction, a global stable
period-3072 branch, a ninth event, universality, TBA membership, homoclinic
geometry, or the full parameter-plane topology.

Manifest:
[`../../experiments/manifests/EXP-316-jones-period3072-solver-relative-criticality.json`](../../experiments/manifests/EXP-316-jones-period3072-solver-relative-criticality.json).

## Result

EXP-316 completes after 7,312.99 seconds. Both solvers independently return the
preregistered stability pattern:

- DOP853 parent/child moduli: `0.9996806831/18.98363348`;
- Radau parent/child moduli: `0.9996553918/18.98308374`.

Thus both numerical representations classify the event-relative sample as a
stable parent with a strongly unstable daughter. Parent and child node RMS
differences are only `4.51e-9` and `3.34e-10`; multiplier relative spreads are
`2.53e-5` and `2.90e-5`. All corrections, direct closure, neutral-mode,
cross-solver, and exact `3584/4096` section gates pass.

The receipt nevertheless fails. DOP853/Radau direct half-period nonclosures
are `9.43e-7/1.61e-6`, both below the frozen `2e-6` primitive-child floor. The
fixed-`a` correction has moved the known daughter closer to its doubled-parent
limit, so its identity is not strong enough for promotion under the existing
gate.

This is strong, solver-consistent evidence for a local subcritical eighth
birth, but it does not change the secure six-supercritical-birth ledger. The
successor must preserve daughter identity through an arclength or explicit
separation constraint and repeat the same event-relative stability audit.

Raw receipt: `artifacts/EXP-316/receipt.json`, 766,025 bytes, SHA-256
`3cf9fa153187e9a82a06f34d5ffc83ec3a547defa0fdd58824ea70e382f2368e`.
Compact receipt: [`receipts/EXP-316.json`](receipts/EXP-316.json).
