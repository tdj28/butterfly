# EXP-193 — Second-component period-6 cycle sample

Status: preregistered; not yet executed

## Question

Can the isolated second-landmark component supply a broad, reproducible set of
approximate period-6 section cycles for the direct two-critical search?

## Frozen computation

EXP-193 binds the full EXP-192 frame and selected 2,598-pixel component by
SHA-256. Starting at the exact second Jones landmark, it chooses 257 component
pixels by deterministic farthest-point sampling in component-range-normalized
`(a,c)` distance. Selection uses geometry only: no symbolic word, return-map
critical, Floquet multiplier, or predicted center enters the sample.

The qualified Float64 GPU crossing kernel independently reintegrates all 257
parameters from `(0,4,0)` using `dt=0.005`, a 2,400-unit transient, and an
800-unit observation window. Each candidate must retain fundamental period 6
under the unchanged blind recurrence classifier and supply at least two full
cycles of finite section crossings. At least 250 of 257 candidates must pass.

Manifest:
[`../../experiments/manifests/EXP-193-second-component-cycle-sample.json`](../../experiments/manifests/EXP-193-second-component-cycle-sample.json).

## Claim boundary

Passing produces approximate six-return cycles suitable for GPU survivor
capture and critical-residual discovery. These are fixed-step attractor tails,
not corrected flow orbits. Any selected center candidate must subsequently
pass DOP853/Radau correction, step refinement, cross-coordinate topology, and
direct critical-membership gates.
