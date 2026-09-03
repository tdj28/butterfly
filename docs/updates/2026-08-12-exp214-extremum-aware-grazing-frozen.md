# EXP-214 freezes the close-crossing-safe grazing qualification

EXP-213 converges the continuous tangency and independent-solver parity but
fails because its standard sign-change collector loses coalescing section
roots. EXP-214 preserves that failure and changes only the counting method:
every monotone interval between successive `y` extrema is root-bracketed
separately.

Four logarithmic offsets on each side and four Radau controls are frozen. A
pass will qualify the event as a local section-representation boundary while
leaving the invariant flip curve free to continue below it under Barrio/orbit
identity.
