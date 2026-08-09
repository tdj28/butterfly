# EXP-158 passes: first primitive stable period-2 child qualified

Date: 2026-08-07

The first fixed-path period-doubling chain now has all of its local gates:

1. EXP-155 follows the same Hopf-born one-winding period-1 family.
2. EXP-156 solves its exact `-1` Floquet event.
3. EXP-157 switches the doubled-cover nullspace onto a nontrivial child.
4. EXP-158 independently proves that the two switch signs are one primitive
   stable period-2 orbit paired with the now-unstable parent.

At the frozen post-event checkpoint `c=3.1845`, Radau finds parent multiplier
`-1.0021368076` and child multiplier `0.9914596621`. Whole-orbit identity,
half-period nonclosure, period ratio, winding, DOP853/Radau parity, and
perturbed-attractor recovery all pass.

For Jones, this changes the first rung from “a plausible crossing on an
L2-like slice” to “a complete local supercritical period-doubling result on an
explicit slice.” The next computation is to continue this child until its own
first `-1` event and repeat the identity-safe switch, while keeping the exact
historical paths and homoclinic endpoint as separate open gates.
