# EXP-206 freezes coupled continuation of the period-6 flip edge

EXP-205 turns seven stability-grid brackets into exact real-minus-one event
seeds. EXP-206 now freezes the next non-raster object: a 41-point fixed-`b`
curve segment obtained by solving the periodic orbit and anti-periodic tangent
together with exact parameter derivatives.

The grid extends beyond both ends of EXP-205, and every point retains both
section identities and an independent monodromy check. A pass will license
period-12 branch switching and boundary-conditioned critical residuals; it
will not identify this flip curve with the TBA curve.

The run passes all 41 points in both directions. It reaches `c=7.16` and
`c=7.32`, with maximum adjacent `a` step `4.64e-6`, maximum coupled orbit
residual `1.10e-11`, and maximum independent flip-multiplier residual
`2.05e-9`. The dense orbit-defined curve is now the qualified parent for
period-12 switching; double-critical and TBA claims remain open.
