# FND-080 — The period-6 flip curve meets a historical-section boundary

Status: qualified broad upper extension; lower grazing nominated for direct refinement

EXP-212 accepts 123 new exact-Jacobian pseudo-arclength points. The complete
upper arm reaches `c=8.40309`. The lower arm stops after 23 points because the
next accurate real-`-1` orbit changes from six to seven crossings on the
historical half-plane, while retaining eight crossings on the Barrio section.
All invariant orbit and Floquet residuals at that rejected point pass.

This is evidence against treating the stop as an endpoint of the
period-doubling curve. It instead nominates a grazing of the historical
section plane at its equilibrium-defined gate. The distinction matters for
Jones: a raster or return-section period label can change while the underlying
flow orbit and its bifurcation persist smoothly.

The result is not yet a qualified grazing because EXP-212 froze only integer
section identities. EXP-213 must prospectively refine the continuous tangency
residual and independently reproduce it under Radau before the mechanism is
promoted.

Evidence:
[`../experiments/EXP-212-period6-flip-pseudoarclength-extension.md`](../experiments/EXP-212-period6-flip-pseudoarclength-extension.md).
