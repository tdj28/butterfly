# EXP-090 — Switch the period-320 flip to period 640

Status: executed; passed candidate gate

Duplicate EXP-089's 32 parent nodes into a 64-segment doubled representation
at the resolved 320→640 event. Derive the primary tangent from the two nearest
EXP-087 parent rows and split the event nullspace. Correct both secondary signs
at frozen normalized steps `0.0005`, `0.001`, `0.002`, and `0.004`.

Pass only if at least one candidate lies on the supercritical side within
`4e-7`, has matching and phase residuals `<=1e-8`, paired half-orbit node RMS
`>=1e-5`, and period ratio within `0.001` of two. Passing establishes a
period-640 candidate only; common-parameter sign identity and block-Floquet
stability remain prospective.

The clean run at `bfbe0ea889b6befe03debd875804a3cddad5e24b` passed. All
eight 64-segment corrections converge with matching residual at most
`1.58e-12`; six candidates inside the frozen parameter window pass every
gate, with both signs represented at three scales. Accepted half-node RMS
ranges from `7.17e-5` to `2.88e-4`, while child/parent period ratios differ
from two by at most `2.53e-9`. Full receipt SHA-256:
`cafd55e04edfd004144dfd9560e244bae5304a78df96958bd35e14c3b8e1c125`.

EXP-091 prospectively corrects both largest accepted signs at one common `b`,
computes 64-segment block-Floquet stability, and performs multiresolution
whole-orbit phase identity before the period-640 rung is called established.
