# EXP-075 — Refine the period-160 flip

Status: executed; failed residual gate

Refine the independently qualified period-160 child's real Floquet crossing
through `-1` inside the frozen EXP-073 bracket
`b=[0.179707248774,0.179714293834]`. Require bracket width `<=4e-13`,
multiplier residual `<=1e-8`, real multiplier, closure `<=1e-9`, and
half-period closure `>=5e-4`.

Passing locates a candidate 160→320 event and supplies another spacing ratio.
Unlike EXP-072, this is a refinement of an already observed branch bracket,
not a blind prediction test. Period-320 existence and criticality remain open.

The clean run at `c6b8e77063fe51c5014a6e9837aa02c8a67b8349` failed one
numerical gate. It narrows the event to `b≈0.17971388330058` in a
`1.05e-13` bracket, with closure `1.10e-12` and half-period closure
`0.0018032`, but the best multiplier residual `1.324e-8` exceeds `1e-8`.
Receipt SHA-256:
`f522a034a367a7251a42eb54e49b0005bf7b714105c35ad39ad014f8eef41c53`.

Retain EXP-075 as failed and withhold its implied spacing ratio. EXP-076
freezes the final bracket and tighter solver settings; no scientific identity
or closure gate is relaxed.
