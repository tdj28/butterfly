# Three different things that can look like a return-map fold

This is a local mathematical explanation of the checks used in EXP-489--491,
not a new empirical result or a claim of a new theorem. It assumes a smooth
flow, a smooth initial curve and the explicitly specified reconstructed
section. It does not establish that this section and curve recover Jones's
original unpublished implementation.

## The short version

We want to assign symbols to branches of a return map. Before doing that, we
must know what the branches actually are. An apparent bend in a sampled plot
can have three different explanations:

| What happened | What the calculation must check | What it permits |
| --- | --- | --- |
| A genuine projected output turn | Smooth event selection, usable input coordinate, output derivative changes sign, nonzero curvature | A local candidate critical point of the projected map |
| A section-grazing boundary | A crossing pair appears or disappears; the selected event can jump | Split the event-domain description; do not interpolate through the jump |
| An input-coordinate turn or severe contraction | Input x derivative reverses or the transported curve becomes numerically tiny | Change/condition the local coordinate; do not count a new output branch |

These mechanisms can coexist near one another. A failed screen is not by
itself a diagnosis of which one occurred. EXP-491 retains its separate flags
for that reason. Its three sampled points cannot exclude hidden boundaries
between them.

## Why event time is part of the derivative

Let the initial curve be q(u), the flow be Phi(t,q), and the section be h=0
with normal n. A particular transverse crossing has a time tau(u), defined
locally by h(Phi(tau(u),q(u)))=0. Write v for the derivative with respect to
u at fixed time, and f for the vector field at the crossing. Differentiating
the section equation gives

    tau_u = -(n . v)/(n . f)
    Q_u   = v + f*tau_u.

Q is the state on the section, so n.Q_u=0. Using v alone differentiates the
wrong object: trajectories at equal time, not their section intersections.
These formulas describe a locally continued transverse root. They do not
guarantee that its ordinal remains the same if another crossing is born
earlier in the trajectory.

For the reconstructed Rössler plane y=y_s, the normal velocity is

    h_t = x + a*y_s.

The negative orientation already requires x < -a*y_s. This is the same
inequality as the historical x gate at the small equilibrium. A newly
reconstructed crossing near the gate is therefore not an outlier that can
be removed solely because its x coordinate differs from the familiar
return-plot band.

## Why a grazing boundary changes the event list

At a grazing point, h=0 and h_t=0. On this plane x=-a*y_s, and direct
differentiation of the Rössler equations gives

    h_tt = x_dot + a*y_dot = -y_s - z.

For a nondegenerate unfolding, h_u and h_tt are both nonzero. To leading
order near (u_star,t_star),

    h = h_u*(u-u_star) + .5*h_tt*(t-t_star)^2 + higher-order terms.

The nearby crossing pair exists on the side where
`-2*h_u*(u-u_star)/h_tt > 0`. Its leading-order time separation is

    2*sqrt(-2*h_u*(u-u_star)/h_tt).

The derivative of each crossing time grows without bound as the pair
approaches tangency. On the other side those two crossings are absent.
Selecting, for example, the fifth negative crossing can then select a
different later event. A large ordinal-return jump is compatible with a
perfectly smooth underlying vector field. It is not automatically an extra
smooth branch of a scalar return map.

EXP-489 tested this local mechanism at two selected witnesses. It did not
locate every grazing boundary in every candidate interval. EXP-491's
time-change and derivative-prediction checks are conservative numerical
screens, not rigorous consequences with universal numerical thresholds.

## Why a zero output derivative is not sufficient

For an input curve after m returns, let

    X(u) = x coordinate of P^m(q(u))
    Y(u) = x coordinate of P^(m+1)(q(u)).

Where the event sequence is smooth and X_u is nonzero, the plotted graph
has derivative dY/dX=Y_u/X_u. A nondegenerate projected fold needs Y_u=0,
X_u nonzero and nonzero second derivative with respect to X. At such a root,

    d²Y/dX² = Y_uu/(X_u)^2.

For the output event on y=y_s, Y_u can be written

    Y_u = v_x - f_x*v_y/f_y.

EXP-490 solves the numerator `f_y*v_x - f_x*v_y = 0`, but then separately
checks transversality, the correct selected event, input conditioning,
opposite neighboring slopes, finite-difference curvature and solver
agreement. These are necessary safeguards: the numerator alone does not
certify a useful scalar fold.

A regular Poincaré map of a smooth flow is locally invertible between its
two-dimensional transverse sections. Its derivative maps a nonzero tangent
to a nonzero tangent. Strong contraction can nevertheless make that tangent
extremely small numerically; its x component can also vanish while the full
tangent does not. A one-dimensional projection can fold even though the
full two-dimensional section map is locally invertible. We must not confuse
a projected fold with loss of invertibility of the flow itself.

## What is still needed for Jones's symbolic chain

The successful right-region projected folds are useful local geometry. They
are not yet a complete symbolic partition. The remaining work has a concrete
order:

1. Describe the domains of consistent transverse event sequences, retaining
   grazing boundaries, input-coordinate failures and unsampled gaps.
2. Establish where different finite-history curves agree as graphs or admit
   a justified quotient. Nearby folds at different upstream u values need
   not be different physical critical points.
3. Qualify the relevant critical geometry and its ordering before assigning
   the C/D and branch dictionary. Do not transport a dictionary from a
   distant parameter value without testing it.
4. Test the resulting conditional coding on held-out returns and corrected
   periodic cycles, without selecting a partition to match target words.
5. Continue the required families between windows to test the claimed
   insertion arrows. Matching isolated node words alone does not verify a
   chain connection.

Until those tests succeed, the flow-level chain is **unverified**, not
verified by a plot and not debunked by a numerical coordinate failure.
The [claim ledger](../claim-ledger.md) records the empirical status; this
derivation does not change any earlier experiment's acceptance rule.
