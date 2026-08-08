# FND-034 — All 22 local unstable-manifold seeds pass

Status: qualified numerical foundation from passed EXP-142

## Finding

Every one of the eleven persistent primitive UPO families supplies a validated
section-tangent unstable direction at both `a=0.148` and `a=0.14825`.

All 22 family-endpoint instances pass, and all 132 combinations of three seed
sizes and two signs reproduce the signed fundamental-lag Floquet amplification.
The worst relative multiplier error is `0.2266%`, the worst transverse leakage
is `0.2198%`, and the largest base lag-return closure is `3.81e-9` in scaled
section coordinates. Section tangent and scaled-normalization residuals remain
at Float64 roundoff.

The validated unstable multipliers range from `3.484` to `2219.278`, so the
library spans weakly through extremely unstable orbit families without a seed
validation failure.

## Consequence

Global unstable-manifold branches can now be traced from every recovered
family without relying on raw flow eigenvectors or arbitrary phase components.
Any subsequent lobe difference must still pass seed-density, seed-size,
return-horizon, attractor-capture, and representation checks. EXP-142 alone
does not identify a pruning, homoclinic, or heteroclinic event.

Tracked receipt: `docs/experiments/receipts/EXP-142.json`.
