# EXP-160 passes; EXP-161 exact period-2 flip frozen

Date: 2026-08-07

EXP-160 passes all preregistered gates on 83 pseudo-arclength points. The
primitive period-2 child remains separated from its period-1 parent by a
minimum half-period closure of `0.2278273`; its winding remains two to
`3.69e-14`. Six independent Radau checks agree with the reference orbits to
at most `3.91e-12` phase-aligned RMS and with their nontrivial multipliers to
at most `2.25e-12`.

The first real `-1` crossing is bracketed between `c=4.292407548657328` and
`c=4.310979132420427`, where the relevant multipliers are `-0.9742030977`
and `-1.0013626600`. This repairs the identity-loss failure of EXP-159; it
does not reinterpret that failed run.

Before solving the event, EXP-161 freezes the EXP-160 receipt hash, bracket,
fixed `(a,b)=(0.1798,0.2)`, eight shooting segments, exact `c` derivatives,
independent Radau verification, period-2 primitivity, and two-winding gates.
Its claim is only the exact period-2-to-4 flip. Switching and qualifying a
period-4 child require successor experiments.
