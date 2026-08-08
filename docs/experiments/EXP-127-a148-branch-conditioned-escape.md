# EXP-127 — Branch-conditioned escape at `a=0.148`

Status: preregistered; not executed

EXP-123 found three branches after 300-unit survivor conditioning but two after
360 units. EXP-124 retained only two at still longer horizons, and independent
PIM in EXP-125 selected two without exponentially discarding initial
conditions. EXP-127 prospectively tests the proposed mechanism: trajectories
visiting the extra, leftmost scalar-map branch should capture by the stable
period-4 attractor sooner than trajectories on the two persistent branches.

The branch definition is frozen from prior rather than new lifetime data. In
the oriented-section `y` projection, all six adequate EXP-123 300-unit runs
resolved two critical points. Their full empirical sensitivity envelopes are
`[-31.382696,-31.074902]` and `[-21.220030,-20.836977]`. A new trajectory is
assigned once, from its last crossing during time 120--150, only if it remains
uncaptured at the time-150 landmark. Points inside either uncertainty envelope
are excluded. Values below the first envelope form the extra branch; the two
remaining certain domains form the pooled core. The earlier paper's “third
branch” therefore means the added branch by count, not the right-to-left scalar
domain index.

New scrambled-Sobol seeds 135--137 each use `2^16` initial conditions through
time 420. Seed 135 is also repeated at half the RK4 step. Every run must retain
at least 100 extra and 5000 core assignments, no integration failure, and no
more than 15% uncertainty-band exclusions. The half-step change in the
extra-minus-core restricted mean capture time must not exceed 15 time units,
and its assigned extra-branch fraction must change by at most 0.01.

The primary effect is extra-minus-core restricted mean survival time over the
270 units following the landmark. A scientific pass requires its 99%
trajectory bootstrap interval to be strictly negative and a two-sided log-rank
`p <= 0.01` independently for all three untouched evidence seeds. Sampling is
one row per trajectory; repeated crossings are not treated as independent.

This can qualify a finite branch-conditioned capture asymmetry. It cannot by
itself establish an infinite-lifetime saddle, a continuous TBA curve, or that
the scalar branch label causes the escape.

Immutable manifest:
`experiments/manifests/EXP-127-a148-branch-conditioned-escape.json`.
