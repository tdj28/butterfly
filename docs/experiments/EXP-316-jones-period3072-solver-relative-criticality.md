# EXP-316 — Solver-relative eighth-birth criticality

Status: frozen; not yet executed

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
