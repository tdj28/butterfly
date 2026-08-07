# EXP-064 — Independently qualify the one-arm period-40 child

Status: executed; passed

At `(a,b,c)=(0.245,0.1798,5.1)`, independently correct the period-20 parent and
the distinct positive-arm period-40 candidate. Require full closures `<=1e-8`,
child half-period closure `>=0.01`, duration ratio within `1e-3` of two,
unstable parent, and stable child.

As an independent attraction test, perturb the child state by the frozen
vector `(1e-4,-1e-4,5e-5)`, integrate for 16 child periods, correct the terminal
state, and require phase-aligned RMS `<=1e-5` to the shooting child with stable
Floquet modulus. Passing establishes a supercritical period-20-to-period-40
flip despite EXP-063's failed symmetric two-arm continuation gate.

The clean run at `23bf5eba6fcdcfaba12067960b48e802d60365d4` passed.
At `b=0.1798`, the period-20 parent has modulus `1.303791`; the period-40
child has modulus `0.263822`, half-period closure `0.032019`, duration ratio
`1.999982`, and closure `5.92e-13`. The frozen perturbed trajectory converges
back to a corrected orbit matching the shooting child to phase-aligned RMS
`1.19e-8`, with the same stable modulus. Receipt SHA-256:
`b1ebd8f4a392bd6680474d982096c1fef920d4da62c71d663e667de06b3eb4ad`.

Accept a supercritical period-20-to-period-40 flip. The positive EXP-063 child
prefix brackets its next `-1` event between `b=0.179702297291` and
`0.179822410665`; refine that candidate next.
