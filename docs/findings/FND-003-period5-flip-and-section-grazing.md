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

EXP-062/064 add a third supercritical rung, 20→40, at
`b=0.1798912237616`. The stable period-40 orbit is also recovered from a
frozen perturbed trajectory, matching the shooting solution to phase-aligned
RMS `1.19e-8`. The emerging cascade is therefore a property of the flow-orbit
families, whereas the intervening 10→11 section-count change remains a
separate representation event.

The first three flip spacings yield descriptive ratios `4.5363` and `4.5944`.
EXP-066 freezes a prospective next-event prediction at `b=0.1797205086405`;
only an independently found period-80 event can test it. With only two ratios,
the project explicitly does not claim Feigenbaum universality.

EXP-068/070 establish a fourth supercritical rung, 40→80. At `b=0.179735`
the stable child is recovered from a perturbed trajectory and has Floquet
modulus `0.005536`. The independently frozen next-event prediction lies inside
the prospective period-80 `-1` bracket, enabling a genuine out-of-sample
scaling test rather than a post-hoc fit.

EXP-072 passes that test: the verified 80→160 event is
`b=0.1797203688505`, only `1.398e-7` from the precommitted prediction. The new
spacing ratio is `4.64763`, closer again to the frozen reference. This is
strong numerical evidence for a classical period-doubling scaling regime on
this local flow-orbit family, but the project still withholds an asymptotic
universality claim pending more rungs, precision studies, and independent
methods.

EXP-073/074 then switch and independently recover the stable period-160 child,
establishing the fifth supercritical rung, 80→160. The child period is about
`1045.88` flow-time units, yet closure remains `1.02e-12` and perturbed-orbit
identity RMS `2.22e-7`.

EXP-077 locates the next `-1` event on that period-160 parent at
`b=0.179713883300532`. The fourth observed spacing ratio is `4.664603`, within
`0.0985%` of the frozen period-doubling reference. This is the closest ratio so
far.

EXP-078 shows why ordinary shooting cannot safely cross that event: the
duration-2092 doubled system loses the flip singular direction. EXP-079
prospectively validates 32-segment multiple shooting, improving the relevant
singular-value resolution by a factor of `854`. EXP-080/081 then calibrate the
new branch-switch procedure against the independently known period-80 child
before it is used at high period.

EXP-082 produces period-320 candidates from both switch signs. EXP-083
independently validates a block-cyclic Floquet calculation against the known
period-80 multiplier to absolute error `4.07e-8`, then finds both fixed-`b`
period-320 representations strongly stable with dominant nontrivial moduli
near `0.05497`. EXP-085 resolves their fractional phase offset and aligns the
whole orbits to RMS `1.19e-8` at phase shift `0.5000000198`. The sixth
supercritical rung, 160→320, is therefore numerically established.

This substantially strengthens the local classical-cascade result and the
methodological case for segmented high-period continuation. It still does not
prove asymptotic Feigenbaum universality, identify the global Jones TBA, or
explain every shrimp in the `(a,c)` plane. Those require additional rungs,
precision/error studies, and continuation of orbit and return-map structures
across parameters rather than extrapolation from one slice.

EXP-086 then made a new prospective prediction using all six verified event
parameters. EXP-087 bracketed the next real `-1` crossing, and EXP-089 resolved
the 320→640 event at `b=0.17971249399393`. The blind prediction missed by only
`3.00e-10`, or `0.0216%` of the new event spacing. The fifth observed spacing
ratio is `4.6681920`, closer again to the frozen reference. This verifies a
second out-of-sample scaling prediction and establishes the seventh flip event;
period-640 existence and stability remain separate prospective tests.
