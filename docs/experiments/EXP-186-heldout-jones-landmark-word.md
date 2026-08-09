# EXP-186 — First held-out Jones landmark word

Status: executed; failed scientifically

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

## Result

The clean run at source commit
`877ee75e77bbbd874bbd4311ebd38f8f14e1ed95` fails the partition-parity and
word gates while passing the reference, orbit-correction, and survivor-profile
gates. The late reference is unambiguously period 6. Independently corrected
DOP853 and Radau orbits close at `1.37e-13` and `2.14e-13`, have the same six
section returns and period `34.465148489`, and agree over the whole orbit to
scaled error `1.23e-9`. The negative conclusion is therefore not an orbit-
integration or periodicity-classification failure.

The factor-two sprinkler comparison is likewise stable. It yields 7,335 and
7,299 survivor-return pairs with no integration failures; the maximum survivor
fraction difference is `0.001465`. Both step sizes resolve x as a robust
two-branch map, with normalized critical-location difference `8.41e-5`, but
resolve z as a monotone one-branch projection. Mandatory x/z parity therefore
fails.

At `dt=0.01`, both orbit solvers encode the x cycle as `010011`; at `dt=0.005`,
both encode it as `C10011`. The change is confined to one orbit point lying at
the empirical critical interval edge. Neither word, nor its reversal up to
cyclic rotation, matches any frozen period-6 target (`CD0000`, `CD0001`,
`CD0010`, `CD0011`, or `CD0111`). The z word is intentionally unresolved
because its scalar projection has no critical point.

Raw receipt SHA-256:
`efae1b0cbee8edf74bf11b6bf3de38c56418c5f8acb454ea3297722d7a836903`.
State artifact SHA-256:
`f58894f952a40857d29b77f12f959001cb05eaa5a9a5eb2e88d1585ddb295731`.
Compact receipt: [`receipts/EXP-186.json`](receipts/EXP-186.json).

## Claim boundary

The printed coordinate was tested exactly. No local refinement, boundary
movement, alphabet permutation, expected word, or word-driven orbit selection
was allowed. EXP-186 rejects using this exact printed gray-box coordinate as a
reproducible Figure 6 word center. It does not reject all published words or
arrows: the printed coordinates are approximate visual landmarks, the source
does not identify them as exact doubly-superstable centers, and the z failure
demonstrates that a scalar projection can be non-injective. The next test must
locate a center from a target-word-blind dynamical objective before encoding
its cycle.
