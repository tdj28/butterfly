# EXP-216 freezes adaptive continuation below the grazing

EXP-215's rejected corrector is inaccurate, not a detected flow event.
EXP-216 changes only the arclength-step policy: failed trials are discarded and
the step is halved, while easy accepted solves permit cautious regrowth. All
orbit, Floquet, section-identity, adjacency, and terminal Radau gates remain
strict.

The frozen target is `c<=6.05` within 120 accepted points. A projection turn is
recorded rather than silently treated as failure, because pseudo-arclength—not
monotone `c`—defines the curve.
