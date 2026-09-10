# When a grazing event inserts one symbol — and when it does not

Conditional local derivation, 2026-09-10. This is a calculus argument with
explicit hypotheses, not a new numerical experiment, a novelty claim, or
verification of Jones's symbolic chains. It explains what the ongoing
periodic-maximum measurements can contribute to that verification.

## 1. A local maximum crossing a plane adds two crossings

Assume a smooth family of nonconstant periodic trajectories and a smooth
section offset. Near one isolated nondegenerate maximum, shift time so the
maximum is at t=0 and write its height above the plane as μ. Assume this
height changes transversely with the family parameter. Uniformly near μ=0,

\[
g(t,\mu)=y(t,\mu)-y_*(\mu)
       =\mu-\frac{\kappa_0}{2}t^2+O(|\mu|t^2+|t|^3),\qquad \kappa_0>0.
\]

The nondegenerate maximum persists by the implicit-function theorem; using
its height as the local parameter requires the stated transverse unfolding.
For sufficiently small μ<0 there is no nearby crossing; μ=0 has one tangency;
μ>0 has two simple crossings,

\[
t_\pm=\pm\sqrt{2\mu/\kappa_0}+O(\mu),\qquad
\dot g(t_\pm)=\mp\sqrt{2\kappa_0\mu}+O(\mu).
\]

One is upward and one downward. To infer the change in the *whole* periodic
crossing count, also require every other crossing to remain transverse,
isolated from this pair, and inside its gate. The local expansion alone says
nothing about unobserved parts of the orbit.

## 2. Why the historical Rössler half-plane retains exactly one

For the implemented Rössler field, y'=x+ay. The small equilibrium satisfies
x*+ay*=0. At any exact crossing y=y*,

\[
 x-x_*=\dot y=\dot g.
\]

Consequently the historical gate x<x* retains the newly born downward
crossing and excludes the upward crossing. Its coordinate approaches the
gate boundary from below as

\[
 x_{\rm new}-x_*=-\sqrt{2\kappa_0\mu}+O(\mu).
\]

This explains a **one-count increase on this half-plane** when the above
hypotheses hold. At the tangency itself x=x*, so the strict gate excludes it;
the Poincaré representation is not regular there. It does not mean a new
physical periodic orbit or a new stable shrimp was created. The same smoothly
continued flow orbit can acquire another recorded section intersection.

## 3. The additional hypotheses needed for a zero in a word

Suppose an independently validated partition labels an interval immediately
below x* with the symbol 0, and its other boundary stays a strictly positive
distance from x*. Then the new crossing lies in that interval for sufficiently
small positive μ, hence contributes a 0. If all existing crossings stay in
their previous partition cells and preserve cyclic order, the new word is
the old word with one 0 inserted at the measured temporal location.

**Neither the label nor the location follows from grazing alone.** To obtain
Jones's specific CDw → CD0w arrow, additionally establish the independent C/D
dictionary, both critical contacts, and that the new crossing falls immediately
after D in the cycle beginning at the same tracked C. A count change, a scalar
fold nearby, or choosing a rotation because it gives the desired word cannot
replace those tests. Exact critical symbols also require a stated limiting or
critical-orbit convention; a generic nearby orbit need not contain exact C/D.

## 4. Ordinary grazing is not a homoclinic return

At a stationary contact with this plane, y=y* and y'=0 imply x=x*. Let
δ=z−z*. Direct substitution into the field gives

\[
F(x_*,y_*,z_*+\delta)
 =(-\delta,\,0,\,(x_*-c)\delta),\qquad y''=-\delta.
\]

For a nondegenerate maximum, δ=κ>0: this is a moving point, not the equilibrium.
As δ→0 the quadratic curvature vanishes, so the nondegenerate local argument
is not uniform in an equilibrium limit. Showing a homoclinic connection instead
requires a full-state approach and the appropriate stable/unstable manifold
connection, with asymptotic and numerical error control. A planar projection
or section tangency does not establish it.

## What is still to measure

The [EXP-520 census](../experiments/receipts/EXP-520-periodic-stationarity-census-result.json)
and [EXP-521 result](../updates/2026-09-10-exp521-critical-response-result.md)
track both inner maxima and all other stationary points. The gaps remain
negative at the tested contact points; this is not yet a crossing birth.
Next maintain qualified fold/orbit geometry, continue the measured extrema
toward zero with error and identity checks, and qualify both sides of any
grazing encountered. Independently locate the partition and temporal insertion
site before comparing a word against Jones. Preserve failed predictors,
unqualified contact tests and changes in section counts; do not censor them
to enforce a desired chain.

The analytic controls in `tests/test_periodic_grazing_symbol_geometry.py`
check the quadratic normal form and exact Rössler identities against the
implemented field. They are not target integrations or evidence that these
hypotheses hold on a Jones connection.
hypotheses hold on a Jones connection.
