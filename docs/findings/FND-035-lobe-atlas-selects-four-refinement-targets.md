# FND-035 — The lobe atlas selects four refinement targets

Status: qualified discovery atlas from passed EXP-143

## Finding

All 396 unstable-manifold traces complete without a return-integration failure.
Independent period-4 attractor cycles pass recurrence below `3.62e-10`, 128
trajectories reach the frozen capture condition, and 23,871 pre-capture section
points remain for lobe analysis.

Every one of the 44 family/sign groups passes. The weakest group still retains
454 pre-capture points; all points lie inside the frozen analysis domain; and
the weakest five-seed coarse grid covers `94.23%` of the nine-seed occupancy
within one cell.

The preregistered score selects four branches for refinement:

1. lower lag-12 family 06, negative sign;
2. lower lag-7 family 03, positive sign;
3. lower lag-5 family 02, positive sign; and
4. lower lag-13 family 07, positive sign.

Their dilated endpoint occupancy Jaccards range from `0.9055` to `0.9843`.
The score is therefore not detecting disjoint lobes. It is influenced by a
larger fraction of seeds reaching stable-cycle capture within 64 returns on
the three-branch side.

## Consequence

The complete atlas does not yet expose a direct broken connection or new lobe.
It supplies a reproducible shortlist and indicates that capture timing, rather
than coarse occupied support, carries much of the endpoint contrast. The four
candidates require denser amplitude sampling, multiple orbit phases, longer
administrative horizons, and direct survival/capture curves before any
pruning or reinjection interpretation.

Tracked receipt: `docs/experiments/receipts/EXP-143.json`.
