# A periodic winding change is useful evidence, but not yet a symbolic chain

This note states the mathematical interpretation used for EXP-494. It adds
no target results and claims no new theorem.

## The geometric statement

Write a phase-parametrized closed orbit as q(s;lambda), 0 <= s <= 1, with
q(0;lambda)=q(1;lambda). Let (x_s(lambda),y_s(lambda)) be the small
equilibrium's projection and define

    X = x - x_s(lambda),  Y = y - y_s(lambda).

If X^2+Y^2 never vanishes, the projected winding number is

    W = (1 / 2*pi) integral [(X dY - Y dX)/(X^2 + Y^2)].

For a closed curve this is an integer. Along a continuous family of closed
curves avoiding the moving origin, the integral changes continuously; an
integer-valued continuous function is constant. Consequently, a change of
winding between two continuously connected periodic orbits requires meeting
the vertical line x=x_s, y=y_s somewhere, or failure of the assumed family
continuity/closure. This argument by itself gives no location of that event.

For the Rössler equations, y'=x+a*y and x_s+a*y_s=0. At that line y'=0, so
the orbit is tangent to the horizontal historical section. At the same
point y''=-y_s-z. Nonzero y'' and nonzero parameter unfolding give a local
crossing-pair birth/death of the form derived in
[the event-geometry note](return-map-geometry-and-symbolic-validation.md).

Crucially, the line is not the equilibrium: z need not equal z_s. A winding
change therefore does **not** establish a homoclinic connection or an orbit
approaching the saddle in three-dimensional distance. Projection and full
three-dimensional orbit topology are different objects.

## Why candidate flow periods need checking

A numerically closed trace can traverse one shorter cycle m times. Counts
on every fixed transverse section then multiply by the same positive integer
m. Thus m divides the greatest common divisor of those counts. For counts
6 and 8, only m=2 remains to be excluded. A nonzero half-period state
separation rules that out for an exact orbit with complete section counts.

Our implementation applies finite numerical separation, closure, repeat and
solver-agreement thresholds. It calls the result a **conditional numerical
minimal-period check**, not a rigorous proof. Missing events, projection
under-resolution and finite precision are still possible failure modes.
The extra check of distinct within-window event states helps detect repeated
traversals independently of the half-period interpolation.

## What would establish more than a count

There are three distinct acceptance questions:

1. **Geometric transition:** corrected, numerically primitive periodic
   samples have differing winding, belong to a qualified continued family,
   and the intervening projected-origin/section tangency is localized.
2. **Symbolic correspondence:** an independently constructed local branch
   partition identifies the relevant C/D critical objects and branches;
   held-out orbits then acquire words without tuning the partition to those
   words. A useful conditional coding need not first be proved a global
   generating partition.
3. **Jones insertion arrow:** independently identified endpoints and the
   intervening mechanism show the proposed inserted symbol in the correct
   ordered itinerary, not merely the right total return count.

The first does not imply the second or third. Two words can have the same
length, and two different sections can count the same orbit differently.
Nor does failure of natural-parameter continuation disprove the family:
folds, strong instability, numerical accuracy and parameter step size may
stop this particular algorithm. Those cases need a distinct continuation or
localization study, not a relabeled successful arrow.
