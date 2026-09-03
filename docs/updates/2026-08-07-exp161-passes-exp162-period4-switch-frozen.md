# EXP-161 passes; EXP-162 period-4 switch frozen

Date: 2026-08-07

EXP-161 locates the exact period-2-to-4 flip at
`(a,b,c)=(0.1798,0.2,4.3100451384813105)`, with period
`T=11.724290361610073`. The coupled multiple-shooting residual is
`1.15e-14`; the reference flip residual is `3.94e-14`. Independent Radau
integration returns a flip residual of `5.91e-13`, closure `1.12e-12`,
half-period nonclosure `2.8615`, and winding `2.0000`. The second exact
period-doubling event on the fixed Jones path is therefore qualified.

EXP-162 is frozen before execution. It forms the doubled period-2 cover,
computes the two-dimensional nullspace of the extended shooting Jacobian,
projects the observed period-2 continuation direction into the primary
tangent, and follows the orthogonal secondary tangent in both signs. Its
preregistered gates require a small second singular value, tangent
independence, closure, separation from the doubled parent, and half-period
nonclosure. Independent period-4 identity, stability exchange, and attraction
remain reserved for a successor qualification experiment.
