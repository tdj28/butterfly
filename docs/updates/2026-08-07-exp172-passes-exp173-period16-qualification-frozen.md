# EXP-172 passes; EXP-173 period-16 qualification frozen

Date: 2026-08-07

EXP-172 passes the geometric period-16 switch in both tangent signs. The
smallest singular value is `5.01e-12`, tangent dot is `6.94e-18`, both arms
contain 24 points, and both remain primitive. Their endpoints are unstable,
showing that the continuation has crossed the narrow child stability window;
endpoint instability is not treated as evidence against local opening.

The recorded arms show a common stable interior interval. EXP-173 is frozen at
`c=4.716`, where both arms have nontrivial half-period separation and strong
local stability. It requires DOP853/Radau identity, phase equivalence of the
two signs, unstable period-8 parent, stable period-16 child, period ratio two,
windings eight and sixteen, and recovery after 64 perturbed child periods.
The smaller `0.01` primitivity floor reflects the directly observed narrow
branch amplitude but remains roughly nine orders above integration closure.
