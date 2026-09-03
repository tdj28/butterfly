# EXP-060 — Qualify the period-20 child at fixed parameter

Status: executed; passed

At `(a,b,c)=(0.245,0.18,5.1)`, independently correct the period-10 parent and
both period-20 switch arms. Require the arms to identify one geometric child
under continuous phase alignment (RMS `<=1e-5`), full closures `<=1e-8`, child
half-period closures `>=0.05`, parent/child duration ratio within `1e-3` of
two, unstable parent, and stable children.

Passing establishes a supercritical period-10-to-period-20 flip at EXP-057 and
closes the second verified rung of the local cascade. Section-crossing counts
are deliberately excluded because their topology changes independently of the
flow-orbit bifurcations.

The clean run at `513dad5afd0d7e6eaf0e52259adf7da258ae143a` passed.
At `b=0.18`, the period-10 parent has modulus `1.389872`; both period-20
children have modulus `0.644636`. The switch arms align after a phase shift of
`0.500153` with RMS `8.88e-7`. Child half-period closures are `0.11595` and
`0.11540`, period ratios are `2.000219`, and all full closures are below
`1.78e-13`. Receipt SHA-256:
`882a46a28da1685b7b1480d495eb03c940e010e3eabd2fbbfa2073a8ca8677cd`.

Accept a supercritical period-10-to-period-20 flip. The accepted EXP-059 branch
prospectively brackets the period-20 child's next `-1` event; refine it without
using section counts.
