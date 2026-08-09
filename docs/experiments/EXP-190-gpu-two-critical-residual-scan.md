# EXP-190 — GPU two-critical residual scan

Status: preregistered; not yet executed

## Question

Among all 65 stable period-6 zero-edge candidates qualified by EXP-189, which
candidate minimizes two separate, survivor-derived distances from the
corrected orbit to the two x critical intervals?

## Frozen computation

The Float64 Triton kernel batches every candidate and the same 2,048 Jones-
section seeds used by EXP-186. It implements the negative y crossing through
the small equilibrium, the historical `x < x_small` half-plane gate, cubic-
Hermite/Newton event localization, period-6 capture, and midpoint return
recording. It runs at RK4 steps `0.01` and `0.005` for 200 time units. The
previously qualified EXP-113 GPU statistical-parity receipt is hash-bound.

The immutable five-variant oracle is applied only to x; EXP-186 already showed
that z is a monotone, non-injective scalar projection in this neighborhood.
An eligible candidate must resolve three branches and two critical intervals
at both steps, produce at least 4,000 survivor pairs and 500 final survivors,
have no failed trajectories, agree in normalized critical midpoints within
`0.03`, agree in its distinct orbit-phase assignment, and have survivor curves
within `0.03`.

The ranking is target-word blind. For each critical interval it measures the
distance from the interval midpoint to a distinct corrected-orbit x value,
normalized by survivor-domain width. It minimizes the worst distance, then the
sum, then the worst assigned zero-slope residual, then candidate ID. At least
three candidates must be eligible; the selected worst midpoint, interval, and
slope residuals must be at most `0.05`, `0.02`, and `0.2`.

Manifest:
[`../../experiments/manifests/EXP-190-gpu-two-critical-residual-scan.json`](../../experiments/manifests/EXP-190-gpu-two-critical-residual-scan.json).

## Claim boundary

A pass is a GPU discovery nomination only. The selected parameter must pass a
separately frozen CPU fixed-step, DOP853, and Radau confirmation before it can
be called doubly superstable or encoded symbolically.
