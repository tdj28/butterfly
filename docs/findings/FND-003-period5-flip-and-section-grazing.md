# FND-003 — A true period-5 flip is followed by a section-boundary grazing

Status: reproduced locally; global relationship to the TBA remains open

At fixed `(a,c)=(0.245,5.1)`, identity-constrained continuation recovers a
true period-5 orbit and locates its `-1` Floquet event at
`b=0.1834675907716` (EXP-050/051). Direct branch switching and independent
qualification establish a supercritical period-5-to-period-10 bifurcation:
below the event the period-5 parent is unstable and a distinct period-10 child
is stable (EXP-052/053).

Farther along the stable child, at `b=0.1817502323206`, the orbit grazes the
boundary of the historical Poincare half-plane (EXP-055). The Rössler equation
`dy/dt=x+a y` implies that an extremum satisfying `y=y_eq` also satisfies
`x=x_eq`; the orbit therefore touches the section plane exactly at its gate
boundary. Its `z≈17.29455` coordinate is far from the small equilibrium. The
Floquet modulus remains `0.141731`, so this is not a loss of orbit stability.

This result supplies a concrete, computable example of the kind of return-map
branch/reinjection change emphasized by Jones. It strengthens that mechanism
as a research target, while remaining narrower than the paper's global hub
claim: one local section grazing does not establish the TBA curve, explain all
shrimp, or prove coordinate-independent topology. It also exposes a numerical
hazard: a standard sign-change event detector can skip both members of the
close crossing pair near grazing. Section counts must be converged in maximum
step or replaced by extremum-aware detection.

The flow-orbit cascade continues independently of that representation change.
EXP-057 locates the stable period-10 child's next `-1` event at
`b=0.1805372082024`; EXP-059/060 switch and independently qualify a stable
period-20 child below it. Thus two successive supercritical rungs, 5→10 and
10→20, are now reproduced with phase-invariant child identity and Floquet
stability exchange. The section grazing lies between their event parameters
but is not either bifurcation.
