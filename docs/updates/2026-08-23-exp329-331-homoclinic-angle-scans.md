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

Tracked receipts: [`../experiments/receipts/EXP-329.json`](../experiments/receipts/EXP-329.json)
and [`../experiments/receipts/EXP-331.json`](../experiments/receipts/EXP-331.json).
Frozen execution commits: `4376c567db9554e858f20a823544996700236abc`
and `f223c95b4f6a2976115e7cff104a52be487f3a00`.
