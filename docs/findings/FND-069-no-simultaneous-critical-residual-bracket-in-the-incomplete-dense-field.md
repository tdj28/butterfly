# FND-069 — No simultaneous critical-residual bracket in the incomplete dense field

Status: qualified finite-sample rejection with an explicit coverage boundary

EXP-199 reconstructs the Barrio positive-x, scalar-z return relation for all
685 individually qualified EXP-198 orbits at two RK4 steps. Of these, 126
retain a robust three-branch map, survivor and critical-location parity, and
one common distinct phase assignment at both steps.

The first signed critical-to-orbit residual changes sign across the eligible
field at both steps. The second residual does not: it remains strictly positive,
with lower bounds `0.031491` and `0.031529`. No candidate passes even one of
the three frozen direct-center gates, and no complete same-assignment lattice
cell brackets both signed residuals. The selected point at
`(a,c)=(0.21559,7.32)` is stable across step halving but remains far outside
the interval and zero-slope gates.

This rejects a double-critical center among the sampled, cross-step-qualified
stable orbits. It does not reject double superstability in the surrounding
period-6 window: the prerequisite mesh failed its coverage gate, its passing
mask is fragmented, and the selected component touches a parameter boundary.
The observed one-sided second residual is therefore a direction-finding result:
the next search must continue the orbit family beyond the qualified mask or
follow its unstable continuation, rather than densify the same rectangle.

Evidence: [`../experiments/EXP-199-incomplete-local-barrio-signed-residual-scan.md`](../experiments/EXP-199-incomplete-local-barrio-signed-residual-scan.md).
