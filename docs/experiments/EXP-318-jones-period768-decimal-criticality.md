# EXP-318 — High-precision criticality audit of the seventh birth

Status: frozen; not yet run

EXP-299 independently corrects the primitive period-1536 daughter under
DOP853 and Radau at `a=0.24070100823781396`. Both solvers classify it as
strongly stable, with moduli `0.12419628/0.12419164`, while their period-768
parent multipliers straddle the unchanged Float64 neutral margin. The shared
coordinate lies `7.24e-14` above EXP-297's passed extrapolated event estimate.

EXP-318 evaluates the corrected DOP853 parent nodes at that exact coordinate
using independent classical-RK4 and RK4 3/8 integrations in 50-decimal-digit
arithmetic. Both tableaux run complete 4,096, 8,192, and 16,384-step profiles
on every one of 1,024 parent segments. Fourth-order and Richardson convergence,
cross-tableau agreement, neutral identity, cyclic spectra, characteristic
residuals, and orbit matching are mandatory. The real-`-1` signal must be at
least `1e-7` and ten times the largest successive-Richardson or cross-tableau
difference.

An unstable parent combined with EXP-299's stable daughter qualifies the
seventh birth as locally supercritical; a stable parent and unstable daughter
would qualify it as subcritical. A neutral or same-side result fails without
relaxation. A pass does not establish a global stable period-1536 branch,
basin measure, universality, TBA membership, homoclinic geometry, or global
parameter-plane topology.

Manifest:
[`../../experiments/manifests/EXP-318-jones-period768-decimal-criticality.json`](../../experiments/manifests/EXP-318-jones-period768-decimal-criticality.json).
