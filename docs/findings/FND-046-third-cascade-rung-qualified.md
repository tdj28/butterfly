# FND-046 — The third fixed-path cascade rung is qualified

Status: passed EXP-164 through EXP-167

## Finding

The primitive period-4 Jones-path child continues without identity loss to an
exact period-4-to-8 flip at
`(a,b,c)=(0.1798,0.2,4.636447200967924)`, with event period
`23.498538844189934`. DOP853 and independent Radau multiplier residuals are
`5.46e-14` and `2.40e-12`; the orbit remains primitive and winds four times.

The doubled-cover switch opens two period-8 arms. At `c=4.65`, independent
Radau gives the unstable period-4 parent multiplier `-1.0874073301` and stable
period-8 child multiplier `0.6466564095`. The arms are the same orbit up to a
near-half-cycle phase shift, with RMS `4.28e-8`; their period ratio is
`2.0000011`, winding is eight, and perturbed integration recovers the child to
RMS `2.59e-9`.

## Implication for Jones

The explicit fixed path now has three complete, independently qualified
supercritical period-doubling rungs through a stable period-8 attractor. This
goes beyond the paper's period-raster evidence and directly demonstrates that
the orbit-continuation logic is extensible through the finite range relevant
to the stated “through period seven” ordering claim.

It still does not establish the claimed symbolic permutation ordering: periods
alone do not determine kneading order or a logistic conjugacy. Exact historical
`L1`/`L2`, a declared return-map partition, and algorithmic symbol comparison
remain required. The equilibrium homoclinic endpoint also remains open.

Tracked receipts: `docs/experiments/receipts/EXP-164.json` through
`docs/experiments/receipts/EXP-167.json`.
