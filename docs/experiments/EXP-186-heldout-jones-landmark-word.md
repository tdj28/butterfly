# EXP-186 — First held-out Jones landmark word

Status: preregistered; not yet executed

## Question

Does the second exact printed Figure 6 landmark, independently classified by
EXP-174 as period 6, produce one of Jones's period-6 words under the immutable
EXP-185 alphabet and a partition reconstructed from nonattracting survivor
data rather than from the target cycle?

## Why landmark 1 is held out

A retrospective engineering pilot used landmark 0 to size a sprinkler and
exposed a representation issue: x resolved two branches, z was monotone, and
the corrected period-5 orbit did not intersect the x critical interval. No
landmark-1 trajectory, return partition, orbit correction, symbol, or word was
examined. EXP-186 freezes landmark index 1 before doing so.

## Frozen design

At `(a,b,c)=(0.21564,0.2,6.124)`, a late DOP853 attractor reference must
reproduce period 6. DOP853 and Radau independently correct the same recurrence
seed; each corrected flow orbit must close below `1e-9`, have exactly six
negative-section returns, and agree after cyclic phase alignment within scaled
state error `1e-6`.

A 2,048-seed section grid is evolved by Float64 RK4 at `dt=0.01` and `0.005`.
Stable-cycle capture is removed and middle-time survivor returns reconstruct
the nonattracting map. Each profile/coordinate needs at least 4,000 return
pairs and must resolve a two- or three-branch partition across five frozen
oracle variants. Survivor fractions may differ by at most `0.03`; critical
locations by at most `0.03` after within-profile normalization. x and z must
return the same branch count.

Only after partition inference and orbit correction does the script attach
the EXP-185 alphabet. A critical letter requires both membership in the
independent critical interval and a worst-variant normalized spline-slope
residual at most `0.15`. All two-step, two-coordinate, two-solver words must
agree up to cyclic rotation and match exactly one of the already hash-bound
period-6 source words. Reversal is reported but not accepted.

Manifest:
[`../../experiments/manifests/EXP-186-heldout-jones-landmark-word.json`](../../experiments/manifests/EXP-186-heldout-jones-landmark-word.json).

## Claim boundary

The printed coordinate is tested exactly. No local refinement, boundary
movement, alphabet permutation, expected word, or word-driven orbit selection
is allowed. A failure may diagnose an approximate/non-superstable landmark or
a non-injective scalar projection; it does not by itself reject every Figure 6
word or arrow.
