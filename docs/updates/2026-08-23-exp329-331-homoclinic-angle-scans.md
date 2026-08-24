# Printed-hub homoclinic angle scans

Date: 2026-08-23

## Result

The first direct global-manifold discovery scans at Jones's approximately
printed hub coordinate pass their execution gates but nominate no homoclinic
return. This is a useful negative search result, not a rejection of Jones's
claim.

EXP-329 launches 96 midpoint angles from a radius-`1e-7` circle in the
two-dimensional unstable eigenspace. Every orbit exits radius `0.01` and is
followed for 400 time units. The closest sampled return reaches
`0.01047463129580855`, but is `0.9992900383572414` transverse to the unique
stable eigendirection. EXP-331 then binds that raw receipt and resolves one
coarse angular spacing on either side with 257 rows. It improves the distance
only to `0.010451007332282615`; the approach remains `0.9992956826043482`
transverse. No row meets both the `0.01` distance and `0.1` transverse-ratio
gates.

EXP-328's NumPy-boolean serialization failure and EXP-330's direct-execution
import failure are preserved. Their successors change only the administrative
defect, not the science configuration.

## Interpretation for Jones

- The local saddle-focus prerequisite remains verified.
- The finite-period family reaching the hub remains distinct from a putative
  equilibrium homoclinic orbit.
- The first finite unstable-manifold scans find close recurrent flybys, but
  their geometry is overwhelmingly transverse rather than stable-aligned.
- The printed coordinate is only approximate and a homoclinic connection is
  codimension one. Failure at exactly `(0.1798,0.2,10.3084)` cannot reject a
  nearby connection on the intended transition segment.
- Uniqueness has not been tested at all.

## Next gate

Replace fixed-coordinate angular gridding with a two-variable
manifold-matching solve in departure angle and `c` at fixed
`(a,b)=(0.1798,0.2)`. Construct both nonlinear local stable-manifold branches
by backward integration, record inward intersections of the returning unstable
manifold with the same sphere, and solve their two tangential mismatch
components. Repeat over shrinking spheres and with an independent integrator
before qualifying a connection. Only after one root is continued over the
declared historical segment can uniqueness receive a bounded test.

## EXP-332 parameter-aware pilot

The first implementation of that gate now passes. Nine `c` slices and 96
angles per slice produce 223 inward intersections with the radius-`0.02`
matching sphere. No direct chord candidate or signed-zero cell is present.
However, the best stable-target chord mismatch decreases monotonically from
`0.0156595` at `c=10.3044` to `0.00656684` at the upper boundary
`c=10.3124`; both signed tangent residuals shrink together and remain
positive. This is the first coherent parameter-direction signal, but not a
root. Hash-bound EXP-333 prospectively extends the unchanged scan through
`c=10.3224`.

## EXP-333 first manifold nominations

The unchanged extension passes with 369 inward sphere intersections. It finds
25 direct chord candidates over `c=10.3184--10.3204`; the best mismatch is
`0.00133787` at `c=10.3194`, about 6.69% of the matching radius. Three coarse
cells contain zero separately in both residual-component ranges. This is the
first encouraging parameter-aware evidence for a nearby connection, but the
componentwise cell rule is not a degree test and two cells have large corner
return-time spreads. EXP-334 therefore freezes an immutable residual-polygon
winding audit before any coupled solve or claim promotion.

## EXP-334 coarse-cell rejection and EXP-335 response

EXP-334 passes and exactly reproduces the three coarse hull cells, but every
residual polygon has winding number zero. Even the cell with only `0.05745`
time units of corner return spread fails the degree test. This rejects the
independent-coordinate rectangle criterion, not the 25 direct near matches.
Because only 28 cells had four radius-`0.02` returns, EXP-335 prospectively
enlarges the sphere to `0.025`, doubles angular resolution, halves `c` spacing,
and builds winding plus a one-time-unit continuity gate directly into the
scan.

## EXP-335 larger-sphere result and orthogonal slice

EXP-335 passes 2,496 rows with 977 inward returns, clearing its coverage gate
at `0.3914`. It finds 141 direct near matches and a best chord mismatch of
`0.00129410` at `c=10.3189`, consistent with the radius-`0.02` minimum, but
all four componentwise hull cells have winding zero. No fixed-`a` root cell is
nominated. The source labels both coordinates approximate and supplies no
endpoint table, so EXP-336 prospectively fixes the printed `c=10.3084` and
scans `a` across `[0.1758,0.1838]` under identical radius, resolution, degree,
and continuity rules.

## EXP-336 coverage failure and sharper orthogonal near miss

EXP-336 completes all 3,264 launches but preserves its sole failed gate: only
309 inward returns give `9.47%` coverage against the frozen 20% requirement.
The broad lower-`a` half supplies no returns. Among completed rows, the
orthogonal slice reduces the best chord to `0.00034435` at `a=0.1828`, 3.76
times below EXP-335's fixed-`a` minimum and only 1.38% of the radius. No degree
cell exists. EXP-337 binds the failed receipt and narrows to the observed
returning band while increasing the matching radius to `0.03`; EXP-336 remains
failed and unreclassified.

Tracked receipts: [`../experiments/receipts/EXP-329.json`](../experiments/receipts/EXP-329.json)
and [`../experiments/receipts/EXP-331.json`](../experiments/receipts/EXP-331.json).
Frozen execution commits: `4376c567db9554e858f20a823544996700236abc`
and `f223c95b4f6a2976115e7cff104a52be487f3a00`.
