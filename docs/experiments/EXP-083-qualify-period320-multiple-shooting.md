# EXP-083 — Independently qualify the period-320 candidate

Status: executed; failed discrete-node identity gate

First validate a block-cyclic Floquet calculation against the ordinary
monodromy result for the independently established period-80 child at
`b=0.179735`. The block method propagates perturbations only over individual
shooting segments; its eigenvalue radii recover full-orbit multiplier moduli
without composing the ill-conditioned duration-2092 monodromy directly.

Then take both accepted EXP-082 switch signs at frozen step `0.005`, correct
them independently with 32-segment fixed-`b` shooting at `b=0.1797132`, and
test whether they are cyclic phase representations of one orbit. Pass only if
the lower-period Floquet modulus agrees within `1e-5`, both high-period
matching residuals are `<=1e-8`, opposite-sign cyclic node RMS is `<=1e-5`,
both half-period distinctness measures are `>=1e-5`, and both dominant
nontrivial block-Floquet moduli are `<=0.999`.

Passing would establish a stable, geometrically identified period-320 cycle
on the supercritical side of the EXP-077 flip. It would close the sixth local
cascade rung numerically; it would still not constitute a rigorous
universality proof.

The clean run at `04fffd6832624ab5856a4f3db84127ab8c81ad44` failed only
the frozen discrete-node identity threshold. The block-Floquet method passed
its independent calibration, reproducing the known period-80 modulus with
absolute error `4.07e-8`. Both fixed-parameter period-320 corrections converge
below `9.90e-13`, agree in period within `2.3e-11`, retain half-period
distinctness, and have strongly stable dominant nontrivial moduli `0.05496991`
and `0.05496954`. However, the best of only 32 cyclic node shifts has RMS
`1.376e-4`, above `1e-5`. Full receipt SHA-256:
`99441eaee59c718fa853e090a608fff9da0e5562ce9cac42dbfc54cfee307d93`.

The two solutions' nearly identical periods, stability, and half-orbit
amplitudes suggest a fractional phase offset that a node-only comparison
cannot resolve. EXP-084 prospectively replaces only that coarse identity
metric with continuous phase alignment built from dense output on each
well-conditioned segment. The original failed gate remains recorded.
