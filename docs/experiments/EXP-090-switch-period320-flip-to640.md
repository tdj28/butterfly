# EXP-090 — Switch the period-320 flip to period 640

Status: preregistered after EXP-089; pending clean execution

Duplicate EXP-089's 32 parent nodes into a 64-segment doubled representation
at the resolved 320→640 event. Derive the primary tangent from the two nearest
EXP-087 parent rows and split the event nullspace. Correct both secondary signs
at frozen normalized steps `0.0005`, `0.001`, `0.002`, and `0.004`.

Pass only if at least one candidate lies on the supercritical side within
`4e-7`, has matching and phase residuals `<=1e-8`, paired half-orbit node RMS
`>=1e-5`, and period ratio within `0.001` of two. Passing establishes a
period-640 candidate only; common-parameter sign identity and block-Floquet
stability remain prospective.
