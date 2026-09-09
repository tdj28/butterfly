# EXP-493: does the grazing add a projected inner turn?

Numerical design and controls prepared while EXP-492 is running, before its
target outcomes are opened. Input binding and source freeze must follow its
complete audit before execution. No target reintegration or paid service:
the data are EXP-492's complete retained side trajectories. This is an
outcome-informed mechanism diagnostic, not independent flow replication.

## Why this is the next scientific question

Jones's reinjection explanation concerns the placement of an additional
inner turn, not just a change in a section-intersection counter. EXP-492
addresses crossing-pair birth/death. This separate diagnostic would test
the geometric link using the same trajectories; it is not independent flow
replication, parameter continuation, or verification of a symbolic arrow.

Let (x_s,y_s,z_s) be the small equilibrium. On the reconstructed section,
h=y-y_s=0 and h_t=x+a*y_s=0 imply x=x_s. Thus every section tangency lies
on the vertical line x=x_s,y=y_s, though z need not equal z_s. The planar
projection passes through its winding origin without the three-dimensional
orbit necessarily reaching the equilibrium. At such a point h_tt=-y_s-z.

Use X=x-x_s and Y=y-y_s. A negative crossing of the section with x<x_s
crosses the negative X ray downward. For a path avoiding (X,Y)=(0,0), an
unwrapped planar angle changes according to

    angle_change = principal_endpoint_difference + 2*pi*downward_ray_crossings

because upward negative-ray crossings cannot occur here: at Y=0, Y'=X<0.
This identity explains a possible link, but computing angle from the same
event count would be circular evidence. The numerical check must instead
sum signed angles of a separately constructed trajectory polygon and compare
its integer branch-cut index with the event census only afterward.

## Complete diagnostic

1. Retain every EXP-492 nomination and every side arm. Failed or skipped
   root/side arms remain explicitly unresolved; do not substitute a new seed.
2. For each eligible root pair, use one common local time window centered
   on the DOP853 root time, with the already specified half-width 0.05. Both
   solvers and all four frozen initial displacements are retained.
3. Construct the planar polygon from retained integration nodes and reported
   y-extrema, not reconstructed crossing roots. Extrema are essential near a
   small loop: ordinary time meshes may jump over its closest approach.
   Interpolate only the two window endpoints with cubic Hermite interpolation
   from stored states and the explicit Rössler vector field. Retain the
   separate ordinary-mesh-only diagnostic, including disagreements.
4. Sum atan2(cross(v_i,v_{i+1}),dot(v_i,v_{i+1})) for vectors from the
   equilibrium projection. Record the maximum angular step, the exact minimum
   distance of each polygon segment to the origin, and the branch-cut integer.
   Compare with a Hermite-midpoint-enriched polygon. No angle is defined at
   the tangency itself. Small radii or unresolved angle steps must fail a
   declared numerical guard, not be clipped or silently unwrapped.
5. Compare both solvers, the two displacement magnitudes, both sides, and the
   separately retained event count. Report the extra planar turn as a
   **relative winding of open arcs**, with the endpoint-angle correction;
   do not describe each local open arc as a closed periodic orbit.
6. Retain the three-dimensional distance from the equilibrium alongside
   projected radius. A vanishing projected radius alone is not a homoclinic
   approach or proof of a new periodic family.

## Frozen numerical rules and retained failures

The augmented and midpoint-enriched polygons must each have minimum segment
radius at least 1e-10, maximum angular step at most 2.9 radians, and integer
branch-cut rounding error at most 1e-10. A segment reaching the origin has
undefined winding and fails explicitly. Both polygon resolutions must agree
on the cut index and angle change within1e-6 radians. This checks the retained
polygon approximation; it does **not** bound all possible hidden smooth
loops between vertices or constitute validated ODE integration.

The polygon cut index must equal the separately counted accepted local
crossings. Paired solvers must agree on the index, angle change within1e-6,
endpoint states within1e-6 after scaling by(15,15,.01), and polygon minimum
radius within1% relative to the larger radius (floor1e-10). For each of the
two opposite-dose pairs, the side with the additional accepted crossing must
have exactly one additional cut index and relative open-arc angle change
within0.01 of one turn. Both solvers and both magnitudes are required.
Qualification also requires the parent EXP-492 boundary to qualify; a failed
parent is not rescued by this diagnostic.

Record all raw-mesh-only disagreements and all polygon vertices. Those
disagreements are anticipated sampling diagnostics, not grounds to erase
an arm. Three-dimensional minimum **polygon-segment** distance is descriptive,
not a rigorous lower bound for the exact trajectory. No radial-scaling
exponent, alphabet, periodic-orbit continuation, or homoclinic verdict is fit.

All 26 parent intervals remain in the result: ten unselected, sixteen
nominated. A failed parent root gate has explicit skipped geometry, while
all available side arms of an eligible root are analyzed even if the parent
side qualification failed. No new seed, integration, alternative window or
threshold adjustment is allowed in this saved-data analysis.

## Controls and reproducibility

Exact analytic data use a parabolic projected arc
X=-(t-1), Y=dose-(t-1)^2/2 at constant z=z_s+13. The stored mesh initially
has only t=.9 and1.1, and the known extremum at t=1 is supplied separately.
The common window is[.95,1.05]. Doses are(-2e-5,-2e-6,2e-6,2e-5); the
positive side has one negative-ray crossing and the negative side none.
Both method labels traverse the actual geometry consumer and comparison
matrix; these are exact arrays, **not solver integrations**. Origin contact
and missing-extremum undersampling are two additional two-label negative
controls. All twelve profile conditions must produce their expected
accept/reject outcomes before the real saved trajectories are analyzed.

The actual controls passed before any EXP-492 target outcome was opened.
`artifacts/EXP-493/preflight-controls-01/controls.json` has SHA-256
`d99853f24e59f8701acb9ca13c1d25ae2bd7e5c6fb01337ba37d70b0e893ef81`.
Twenty-three focused tests passed, covering analytic circles in both
orientations, origin/near-origin/undersampling rejection, exact cubic Hermite
interpolation, full side matrices and injected geometry/event disagreements.
Before opening the parent results, the known open-arc angle oracle was also
checked against its explicit formula, not only its winding integer. A second
control run at `preflight-controls-02` produced the exact same JSON bytes.

The now-completed parent binds all 248 IVPs, including its one retained
paired-state accuracy failure. Its full-summary SHA-256 is
`4a856360eb1c8da8099fd39ca09e4543423ed32a8a4dd20766f175a7c98e86a6`;
its public-result SHA-256 is
`7544eb230106e6b1f6fccf658fb6f60e6ef53230bcc0709b0b6e912addc268bf`.
These anchors were added after the parent audit, with no changes to the
previously designed geometric windows, numerical guards or selection matrix.
The final focused suite passes 31 tests, including immutable numerical/input
anchors and the complete exact-data control matrix. The complete local suite
passes **2,051 tests with one Linux-only skip in 131.98 seconds**. No EXP-493
target geometry was opened to obtain these results.

Before execution bind the exact complete EXP-492 summary and public receipt,
freeze/push this protocol, the manifest, consumer, geometry module and tests,
and verify the live remote source. The consumer replays the complete parent
raw-data audit first. It repeats controls, writes a separate binding and
complete result, then supports a second read-only raw-to-result replay.
All old trajectories and thresholds remain immutable.

Use the existing CPU with zero new integrations or paid services. Require
the full read-only computation to finish within300 seconds before accepting
its result, and limit the generated result to32 MiB. No timer-driven retry or
alternate input selection is allowed. A failed analysis retains the parent
data and any local failure output; it does not consume or reset a flow run.

The eventual inference is conditional on this section/projection, not a
topological invariant of the full three-dimensional flow and not an
assignment of Jones's C/D/0/1/2 alphabet. Same-agent replay and two numerical
solvers are not independent researchers or peer review.
